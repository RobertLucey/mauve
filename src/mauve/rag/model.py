import logging
import os
from functools import partial
from pathlib import Path

import pandas
import torch

from datasets import (
    Features,
    Sequence,
    Value,
    load_dataset,
    load_from_disk
)

import faiss
from transformers import (
    DPRContextEncoder,
    DPRContextEncoderTokenizerFast,
    RagRetriever,
    RagSequenceForGeneration,
    RagTokenizer,
)

from mauve.constants import RAG_PATH
from mauve.utils import iter_books

logger = logging.getLogger('mauve')

torch.set_grad_enabled(False)


def split_documents(documents: dict) -> dict:
    return documents


def embed(
    documents: dict,
    ctx_encoder: DPRContextEncoder,
    ctx_tokenizer: DPRContextEncoderTokenizerFast,
    device: str
) -> dict:
    input_ids = ctx_tokenizer(
        documents['title'],
        documents['text'],
        truncation=True,
        padding='longest',
        return_tensors='pt'
    )['input_ids']
    embeddings = ctx_encoder(
        input_ids.to(device=device),
        return_dict=True
    ).pooler_output
    return {
        'embeddings': embeddings.detach().cpu().numpy()
    }


class RAGModel():

    def __init__(self, name: str, max_lines=50000, includes=None, **kwargs) -> None:
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.name = name
        self.max_lines = max_lines
        self.includes = includes

        self.model = None
        self.tokenizer = None
        self.dataset = None

        self.context_encoder = kwargs.get(
            'context_encoder',
            'facebook/dpr-ctx_encoder-multiset-base'
        )

        self.rag_sequence = kwargs.get(
            'rag_sequence',
            'facebook/rag-sequence-nq'
        )

        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    def generate_csv(self) -> None:
        logger.debug('generating rag csv: %s', self.name)
        to_write = []
        for idx, book in enumerate(iter_books()):
            if len(to_write) >= self.max_lines:
                break
            if self.includes is not None:
                if self.includes not in book.raw_content.lower():
                    continue
            for sentence in book.sentences:
                if len(to_write) >= self.max_lines:
                    break
                if not sentence.strip():
                    continue
                for sub_sentence in sentence.split('\n'):
                    if not sub_sentence.strip():
                        continue
                    if len(sub_sentence.split()) < 2 or len(sub_sentence.split()) > 30:
                        continue

                    if self.includes is not None:
                        if self.includes in sub_sentence.lower():
                            print('ADDING')
                            to_write.append({
                                'title': book.title,
                                'text': sub_sentence.strip(),
                            })
                    else:
                        to_write.append({
                            'title': book.title,
                            'text': sub_sentence.strip(),
                        })

        pandas.DataFrame(to_write).to_csv(
            self.csv_path,
            index=False
        )

    def load_dataset(self) -> None:
        logger.debug('loading rag dataset: %s', self.name)

        self.dataset = load_dataset(
            'csv',
            data_files=[self.csv_path],
            split='train',
            delimiter=',',
            column_names=['title', 'text']
        )

        self.dataset = self.dataset.map(
            split_documents,
            batched=False,
            num_proc=6,
            batch_size=100,
        )

        ctx_encoder = DPRContextEncoder.from_pretrained(
           self.context_encoder
        ).to(device=self.device)
        ctx_tokenizer = DPRContextEncoderTokenizerFast.from_pretrained(
            self.context_encoder
        )
        new_features = Features(
            {
                'text': Value('string'),
                'title': Value('string'),
                'embeddings': Sequence(Value('float32'))
            }
        )  # optional, save as float32 instead of float64 to save space

        self.dataset = self.dataset.map(
            partial(
                embed,
                ctx_encoder=ctx_encoder,
                ctx_tokenizer=ctx_tokenizer,
                device=self.device
            ),
            batched=True,
            batch_size=16,
            features=new_features,
        )

        self.dataset.save_to_disk(self.dataset_path)

        index = faiss.IndexHNSWFlat(
            768,
            128,
            faiss.METRIC_INNER_PRODUCT
        )
        self.dataset.add_faiss_index(
            'embeddings',
            custom_index=index
        )

        self.dataset.get_index('embeddings').save(self.faiss_path)

    def load_model(self) -> None:
        logger.debug('loading rag retriever: %s', self.name)
        retriever = RagRetriever.from_pretrained(
            self.rag_sequence,
            index_name='custom',
            indexed_dataset=self.dataset
        )
        logger.debug('loading rag model: %s', self.name)
        self.model = RagSequenceForGeneration.from_pretrained(
            self.rag_sequence,
            retriever=retriever
        )

    def load_tokenizer(self) -> None:
        logger.debug('loading rag tokenizer: %s', self.name)
        self.tokenizer = RagTokenizer.from_pretrained(
            self.rag_sequence
        )

    def load(self, regenerate=False) -> None:
        if os.path.exists(self.dataset_path) and regenerate is False:
            self.dataset = load_from_disk(self.dataset_path)
            self.dataset.load_faiss_index('embeddings', self.faiss_path)
        else:
            self.generate_csv()
            self.load_dataset()
        self.load_model()
        self.load_tokenizer()

    def ask(self, question: str) -> str:
        input_ids = self.tokenizer.question_encoder(
            question,
            return_tensors='pt'
        )['input_ids']
        generated = self.model.generate(input_ids)
        generated_string = self.tokenizer.batch_decode(
            generated,
            skip_special_tokens=True
        )[0]
        logger.debug('Q: %s\t\t\tA: %s', question, generated_string)
        return generated_string

    @property
    def actual_name(self) -> str:
        if self.includes is None:
            return '%s_%s' % (self.name, self.max_lines)
        return '%s_%s_%s' % (self.name, self.includes, self.max_lines)

    @property
    def faiss_path(self) -> str:
        return os.path.join(
            self.output_dir,
            'my_knowledge_dataset_hnsw_index.faiss'
        )

    @property
    def dataset_path(self) -> str:
        return os.path.join(
            self.output_dir,
            self.actual_name
        )

    @property
    def csv_path(self) -> str:
        return os.path.join(
            self.output_dir,
            '{}.csv'.format(self.actual_name)
        )

    @property
    def output_dir(self):
        return os.path.join(RAG_PATH, self.actual_name)

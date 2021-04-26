from unittest import TestCase

from transformers import (
    DPRContextEncoder,
    DPRContextEncoderTokenizerFast
)

from mauve.rag.model import (
    embed,
    RAGModel
)


class TestModel(TestCase):

    def test_embed(self):

        ctx_encoder = DPRContextEncoder.from_pretrained(
           'facebook/dpr-ctx_encoder-multiset-base'
        ).to(device='cpu')
        ctx_tokenizer = DPRContextEncoderTokenizerFast.from_pretrained(
           'facebook/dpr-ctx_encoder-multiset-base'
        )

        self.assertEqual(
            len(embed(
                {
                    'title': 'something',
                    'text': 'blah'
                },
                ctx_encoder,
                ctx_tokenizer,
                'cpu'
            )['embeddings'][0]),
            768
        )

    def test_generate_csv(self):
        pass

    def test_load_dataset(self):
        pass

    def test_load_model(self):
        pass

    def test_load_tokenizer(self):
        pass

    def test_load(self):
        pass

    def test_ask(self):
        pass

    def test_props(self):
        model = RAGModel(
            name='something',
            max_lines=10
        )
        self.assertEqual(
            model.output_dir,
            '/tmp/mauve/rag/something_10'
        )
        self.assertEqual(
            model.csv_path,
            '/tmp/mauve/rag/something_10/something_10.csv'
        )
        self.assertEqual(
            model.dataset_path,
            '/tmp/mauve/rag/something_10/something_10'
        )
        self.assertEqual(
            model.faiss_path,
            '/tmp/mauve/rag/something_10/my_knowledge_dataset_hnsw_index.faiss'
        )

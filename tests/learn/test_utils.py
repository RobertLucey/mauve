from unittest import TestCase

from gensim import utils
from gensim.models.doc2vec import TaggedDocument
from gensim.models import Doc2Vec


class TestLearnUtils(TestCase):

    def test_get_train_test(self):

        from mauve.learn.utils import get_train_test

        model = Doc2Vec(
            min_count=5,
            window=10,
            vector_size=1,
            sample=1e-4,
            negative=5,
            workers=7
        )

        docs = []
        docs.extend(
            [
                TaggedDocument(
                    utils.to_unicode('this is some other content').split(), ['else_%s' % i]
                ) for i in range(50)
            ]
        )
        docs.extend(
            [
                TaggedDocument(
                    utils.to_unicode('this is some content').split(), ['something_%s' % (i)]
                ) for i in range(100)
            ]
        )

        model.build_vocab(docs)

        train_arrays, train_labels, test_arrays, test_labels = get_train_test(
            model,
            {
                'something': list(range(100)),
                'else': list(range(50))
            }
        )
        self.assertEqual(
            train_labels.tolist(),
            [0] * 80 + [1] * 40
        )
        self.assertEqual(
            test_labels.tolist(),
            [0] * 20 + [1] * 10
        )

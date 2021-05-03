import logging
from collections import defaultdict
from typing import Mapping

import numpy as np

from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    AdaBoostClassifier
)
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression

from mauve.utils import iter_books

from mauve.learn.utils import get_train_test

logger = logging.getLogger('mauve')


def get_classifiers() -> Mapping:
    return {
        'nearest_neighbors': KNeighborsClassifier(3),
        'linear_svm': SVC(kernel='linear', C=0.025),
        'rbf_svm': SVC(gamma=2, C=1),
        'decision_tree': DecisionTreeClassifier(max_depth=5),
        'random_forest': RandomForestClassifier(
            max_depth=5,
            n_estimators=10,
            max_features=1
        ),
        'neural_net': MLPClassifier(alpha=1, max_iter=100000),
        'adaboost': AdaBoostClassifier(),
        'naive_bayes': GaussianNB(),
        'qda': QuadraticDiscriminantAnalysis(),
        'logistic_regression': LogisticRegression(max_iter=10000)
    }


class ClassifierCreator():

    def __init__(
        self,
        model,
        tagged_docs,
        num_items=0,
        equalize_group_contents=False,
        train_ratio=0.8,
        epochs=10
    ):
        """

        :param model: An init'd Doc2Vec model
        :param tagged_docs: class of tagged docs.
            Books given to this will be split by some tag.
            Example: NationalityTaggedDocs will split books into the
                     nationality of the author
        :kwarg num_items: The number of books to have processed in order to
            move onto training
        :kwarg equalize_group_contents: Ensure that the number of items in each
            tag are proportional. Will chop the excess from groups with more
            items than the minimum
        :kwarg train_ratio: What proportion to use for training
        :kwarg epochs: How many epochs to train whatever the given model is
        """
        self.model = model
        self.tagged_docs = tagged_docs
        self.num_items = num_items
        self.equalize_group_contents = equalize_group_contents
        self.train_ratio = train_ratio
        self.epochs = epochs

        self.classifiers = {}
        self.class_group_map = {}

    def load_tagged_docs(self) -> None:
        # TODO: change this, it's a bit bookey rather than texty
        processed = 0
        for item in iter_books():
            if len(self.tagged_docs.items) >= self.num_items:
                break
            self.tagged_docs.load(item)
            processed += 1

    def generate_classifier(self) -> None:

        logger.debug('Start loading content')

        self.load_tagged_docs()
        self.tagged_docs.clean_data()

        logger.debug('Using %s books', len(self.tagged_docs.items))

        logger.debug('Start loading content into model')
        self.model.build_vocab(self.tagged_docs.to_array())

        logger.debug('Start training model')
        self.model.train(
            self.tagged_docs.perm(),
            total_examples=self.model.corpus_count,
            epochs=self.epochs
        )

        grouped_vecs = defaultdict(list)
        for tag in self.model.docvecs.key_to_index.keys():
            if len(tag.split('_')) > 2:
                continue
            grouped_vecs[tag.split('_')[0]].append(int(tag.split('_')[1]))

        train_arrays, train_labels, test_arrays, test_labels, class_group_map = get_train_test(
            self.model,
            grouped_vecs,
            equalize_group_contents=self.equalize_group_contents,
            train_ratio=self.train_ratio
        )

        logger.debug('Class to group map: %s', class_group_map)

        classifiers = get_classifiers()

        # TODO: Try fit by individual class too rather than on the whole

        for name, clf in classifiers.items():
            try:
                clf.fit(train_arrays, train_labels)
                score = clf.score(test_arrays, test_labels)
                logger.info('%s %s', name, score)

                joined = [i for i in zip(test_labels, test_arrays)]
                class_arrays_map = defaultdict(list)
                for test_label, test_array in joined:
                    class_arrays_map[test_label].append(test_array)

                for label, array in class_arrays_map.items():
                    score = clf.score(np.array(array), len(array) * [label])
                    logger.info('%s %s', class_group_map[label], score)

                logger.info('----------')

                classifiers[name] = clf
            except ValueError as ex:
                logger.error('Failed to use classifier "%s": %s', name, ex)
                classifiers[name] = None

        self.classifiers = classifiers
        self.class_group_map = class_group_map

        # TODO: get the best classifier and use that in future
        self.preferred_classifier = self.classifiers['neural_net']

    # TODO: make a score thing that gives back a number like age

    def predict(self, content: str) -> str:
        return self.class_group_map[
            self.preferred_classifier.predict(
                [self.model.infer_vector(content.split())]
            )[0]
        ]

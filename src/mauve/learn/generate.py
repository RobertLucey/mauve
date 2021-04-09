import logging
from collections import defaultdict

from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
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


def get_classifiers():
    return {
        'nearest_neighbors': KNeighborsClassifier(3),
        'linear_svm': SVC(kernel='linear', C=0.025),
        'rbf_svm': SVC(gamma=2, C=1),
        'gaussian_rprocess': GaussianProcessClassifier(1.0 * RBF(1.0)),
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


def generate_model(
    model,
    tagged_docs,
    num_books=0,
    equalize_group_contents=False,
    classifier=None,
    train_ratio=0.8,
    epochs=10
):
    """

    :param model: An init'd Doc2Vec model
    :param tagged_docs: class of tagged docs.
        Books given to this will be split by some tag.
        Example: NationalityTaggedDocs will split books into the
                 nationality of the author
    :kwarg num_books: The number of books to have processed in order to
        move onto training
    :kwarg equalize_group_contents: Ensure that the number of items in each
        tag are proportional. Will chop the excess from groups with more
        items than the minimum
    :kwarg classifier: Classifier object, uses a flight of classifiers if
        none specified
    :kwarg train_ratio: What proportion to use for training
    :kwarg epochs: How many epochs to train whatever the given model is
    """

    logger.debug('Start loading content')
    processed = 0
    for book in iter_books():
        if len(tagged_docs.books) >= num_books:
            break
        tagged_docs.load(book)
        processed += 1

    tagged_docs.clean_data()

    logger.debug('Using %s books', len(tagged_docs.books))

    logger.debug('Start loading content into model')
    model.build_vocab(tagged_docs.to_array())

    logger.debug('Start training model')
    model.train(
        tagged_docs.perm(),
        total_examples=model.corpus_count,
        epochs=epochs
    )

    grouped_vecs = defaultdict(list)
    for tag in model.docvecs.doctags.keys():
        if len(tag.split('_')) > 2:
            continue
        grouped_vecs[tag.split('_')[0]].append(int(tag.split('_')[1]))

    train_arrays, train_labels, test_arrays, test_labels, class_group_map = get_train_test(
        model,
        grouped_vecs,
        equalize_group_contents=equalize_group_contents,
        train_ratio=train_ratio
    )

    logger.debug('Class to group map: %s', class_group_map)

    classifiers = get_classifiers()

    # TODO: Try fit by individual class too rather than on the whole

    logger.debug('Start classifying')
    if classifier is not None:
        clf = classifiers[classifier]
        clf.fit(train_arrays, train_labels)
        return clf

    for name, clf in classifiers.items():
        try:
            clf.fit(train_arrays, train_labels)
            score = clf.score(test_arrays, test_labels)
            logger.info('%s %s', name, score)
            classifiers[name] = clf
        except ValueError as ex:
            logger.error('Failed to use classifier "%s": %s', name, ex)
            classifiers[name] = None
    return classifiers


#from gensim.models import Doc2Vec
#from mauve.learn.tagged_docs import (
#    AuthorTaggedDocs,
#    GenderTaggedDocs,
#    NationalityTaggedDocs
#)
#generate_model(
#    Doc2Vec(
#        min_count=5,
#        window=10,
#        vector_size=150,
#        sample=1e-4,
#        negative=5,
#        workers=7
#    ),
#    NationalityTaggedDocs(
#        min_per_group=50
#    ),
#    num_books=10000
#)

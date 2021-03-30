import logging
from collections import defaultdict

from gensim.models import Doc2Vec

from sklearn.linear_model import LogisticRegression

from mauve.utils import iter_books

from mauve.learn.utils import get_train_test
from mauve.learn.tagged_docs import (
    AuthorTaggedDocs,
    GenderTaggedDocs
)

from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis


logger = logging.getLogger('mauve')



def generate_model(
    model,
    grouper,
    num_books=0,
    equalize_group_contents=False,
    classifier=None,
    train_ratio=0.8,
    epochs=10
):

    logger.debug('Start loading content')
    tagged_docs = grouper()
    processed = 0
    for idx, book in enumerate(iter_books()):
        if len(tagged_docs.books) >= num_books:
            break
        tagged_docs.load(book)
        processed += 1

    tagged_docs.clean_data()

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

    train_arrays, train_labels, test_arrays, test_labels = get_train_test(
        model,
        grouped_vecs,
        equalize_group_contents=equalize_group_contents,
        train_ratio=train_ratio
    )

    classifiers = {
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


#generate_model(
#    Doc2Vec(
#        min_count=5,
#        window=10,
#        vector_size=150,
#        sample=1e-4,
#        negative=5,
#        workers=7
#    ),
#    model,
#    AuthorTaggedDocs,
#    num_books=1000,
#    equalize_group_contents=True
#)

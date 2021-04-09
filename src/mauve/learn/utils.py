import logging
from collections import defaultdict

import numpy as np

logger = logging.getLogger('mauve')


def get_train_test(
    model,
    grouped_vecs,
    equalize_group_contents=False,
    train_ratio=0.8
):
    """
    Split into train and test data for each given group

    :kwarg grouped_vecs: {group_name: [0, 1, ...], group_name_2: [0, 1, ...]}
            dict of things to group by with a list elements for use in
            equalizing the number of items for each group
    :kwarg equalize_group_contents: To have the same number of items
            in each group
    :kearg train_ratio:
    :return: train_arrays, train_labels, test_arrays, test_labels
    """

    def format_arrays_labels(split_type):
        logger.debug('Creating %s data', split_type)
        arrays = np.zeros(
            (
                sum([len(v) for k, v in splits.items() if k.split('_')[-1] == split_type]),
                model.vector_size
            )
        )
        labels = np.zeros(
            sum([len(v) for k, v in splits.items() if k.split('_')[-1] == split_type])
        )

        class_group_map = {}
        next_idx = 0
        for group_type, vects in splits.items():
            if group_type.split('_')[-1] != split_type:
                continue
            for vect in vects:
                arrays[next_idx] = model.docvecs['%s_%s' % (group_type.split('_')[0], vect)]
                labels[next_idx] = list(grouped_vecs.keys()).index(group_type.split('_')[0])
                class_group_map[list(grouped_vecs.keys()).index(group_type.split('_')[0])] = group_type.split('_')[0]
                next_idx += 1

        return (
            arrays,
            labels,
            class_group_map
        )

    logger.debug('Splitting training / test data')
    if equalize_group_contents:
        min_count = min([len(v) for v in grouped_vecs.values()])
        logger.debug(
            'Equalizing lengths of input groups. Setting min to %s',
            min_count
        )
        grouped_vecs = {
            k: sorted(v)[0:min_count] for k, v in grouped_vecs.items()
        }

    splits = defaultdict(dict)
    for group_name, vects in grouped_vecs.items():
        train, test = np.split(
            vects,
            [int(len(vects) * train_ratio)]
        )
        splits[group_name + '_train'] = sorted(train)
        splits[group_name + '_test'] = sorted(test)

    train_arrays, train_labels, _ = format_arrays_labels('train')
    test_arrays, test_labels, class_group_map = format_arrays_labels('test')

    return (
        train_arrays,
        train_labels,
        test_arrays,
        test_labels,
        class_group_map
    )

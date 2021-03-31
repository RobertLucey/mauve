"""
Get distinctive words by whatever group

Uses the percentage usage rather than count since a long book about
    sunflowers could skew things a fair bit
"""

from collections import defaultdict

import numpy

from mauve.utils import (
    iter_books,
    round_down
)


class BaseWordUsage:

    def __init__(
        self,
        method=None,
        only_words=None,
        only_groups=None,
        head_tail_len=10,
        print_rate=100,
        required_genre=None,
        required_lang=None,
        required_safe_to_use=None
    ):
        """

        :kwarg method: by_word or by_book on which to process usage of a word
            by_word - if there are 100 words in a book and 1 is the word you're
                      looking for the score will be 0.01
            by_book - if there are 100 words in a book and 1 is the word you're
                      looking for the score will be 1
        :kwarg only_words: Only include these words as interesting
        :kwarg only_groups: Only include data of groups in this list
        :kwarg head_tail_len: How many words to give back for each comparison
        :kwarg print_rate: After how many books processed to print the stats
        :kwarg required_genre:
        :kwarg required_lang:
        :kwarg required_safe_to_use:
        """
        self.method = method
        self.only_words = only_words
        self.only_groups = only_groups
        self.head_tail_len = head_tail_len
        self.print_rate = print_rate
        self.groups = defaultdict(dict)
        self.prevs = defaultdict(int)

        self.required_genre = required_genre
        self.required_lang = required_lang
        self.required_safe_to_use = required_safe_to_use

    def grouper(self, book):
        raise NotImplementedError()

    def update_groups(self, book):
        group_names = set(self.grouper(book))
        if self.only_groups is not None:
            group_names = group_names.intersection(set(self.only_groups))
        if group_names == set():
            return None

        counts = book.get_word_counts(only_include_words=self.only_words)
        local_words = counts.keys()
        tot = len(book.words)

        for group_name in group_names:
            if self.only_words is None:
                # TODO: take global words from all groups
                global_words = self.groups[group_name].keys()
                for missing_word in set(global_words) - set(list(local_words)):
                    counts[missing_word] = 0
            else:
                for missing_word in set(self.only_words) - set(list(local_words)):
                    counts[missing_word] = 0

            for word, times_used in counts.items():
                try:
                    if self.method == 'by_book':
                        self.groups[group_name][word].append(1)
                    elif self.method == 'by_word':
                        self.groups[group_name][word].append(times_used / tot)
                    else:
                        raise Exception()
                except KeyError:
                    if self.method == 'by_book':
                        self.groups[group_name][word] = [0] * self.prevs[group_name] + [1]
                    elif self.method == 'by_word':
                        self.groups[group_name][word] = [0] * self.prevs[group_name] + [times_used / tot]
                    else:
                        raise Exception()

            self.prevs[group_name] += 1

    def get_stats(self, verbose=False):
        alt_groups = defaultdict(dict)
        for key in self.groups.keys():

            alt_groups[key] = {
                o[0]: numpy.mean(o[1]) for o in sorted(
                    self.groups[key].items(),
                    key=lambda item: numpy.mean(item[1]),
                    reverse=True
                ) if any([
                    len([i for i in o[1] if i != 0]) / len(o[1]) < 0.9,
                    len([i for i in o[1] if i != 0]) / len(o[1]) > 0.05
                ])
            }

        results = []
        for base_group in alt_groups.keys():
            if base_group is None:
                continue
            base_keys = list(alt_groups[base_group].keys())
            for cmp_group in alt_groups.keys():
                if cmp_group is None or cmp_group == base_group:
                    continue

                words_data = {}
                for word in base_keys + list(alt_groups[cmp_group].keys()):
                    words_data[word] = alt_groups[base_group].get(word, 0) - alt_groups[cmp_group].get(word, 0)

                if verbose:
                    data = [
                        (i[0], i[1]) for i in sorted(
                            words_data.items(),
                            key=lambda item: item[1]
                        )[:self.head_tail_len]
                    ]
                else:
                    data = [
                        i[0] for i in sorted(
                            words_data.items(),
                            key=lambda item: item[1]
                        )[:self.head_tail_len]
                    ]

                results.append(
                    (
                        cmp_group,
                        base_group,
                        data
                    )
                )
        return results

    def print_stats(self, verbose=False):
        for cmp_group, base_group, data in self.get_stats(verbose=verbose):
            print(
                '%s < %s: %s' % (
                    base_group,
                    cmp_group,
                    data
                )
            )

    def process(self, verbose=False):
        for idx, book in enumerate(iter_books()):
            # Maybe only update prev if update_groups did anything.
            # Doesn't really matter
            self.update_groups(book)
            if idx % self.print_rate == 0:
                self.print_stats(verbose=verbose)

    def get_is_usable(self, book):
        """
        Get if the given book passes the requirements to be
        included in the data.
        """
        if (self.required_genre and not book.is_genre(self.required_genre)) or (self.required_safe_to_use and not book.safe_to_use) or (self.required_lang and not book.lang == self.required_lang) or (not book.has_content):
            return False
        return True


class AuthorGenderWordUsage(BaseWordUsage):
    """
    Generally want to use by_word method
    """

    def grouper(self, book):
        groups = []
        if self.only_groups is not None:
            if book.author.gender not in self.only_groups:
                return []
        if self.get_is_usable(book):
            groups.append(book.author.gender)
        return groups


class AuthorNationalityWordUsage(BaseWordUsage):

    def grouper(self, book):
        groups = []
        if self.only_groups is not None:
            if book.author.nationality not in self.only_groups:
                return []
        if self.get_is_usable(book):
            groups.append(book.author.nationality)
        return groups


class AuthorDOBWordUsage(BaseWordUsage):

    def grouper(self, book):
        groups = []
        if self.only_groups is not None:
            if round_down(book.author.birth_year, 10) not in self.only_groups:
                return []
        if self.get_is_usable(book):
            if book.author.birth_year:
                groups.append(round_down(book.author.birth_year, 25))
        return groups


class PublishedYearWordUsage(BaseWordUsage):

    def grouper(self, book):
        groups = []
        if self.only_groups is not None:
            if round_down(book.year_published, 10) not in self.only_groups:
                return []
        if self.get_is_usable(book):
            if book.year_published is not None:
                groups.append(round_down(book.year_published, 10))
        return groups


class GenreWordUsage(BaseWordUsage):

    def grouper(self, book):
        groups = []
        if self.get_is_usable(book):
            if self.only_groups is not None:
                return set([t.name for t in book.tags]).intersection(set(self.only_groups))
            groups.extend([t.name for t in book.tags])
        return groups

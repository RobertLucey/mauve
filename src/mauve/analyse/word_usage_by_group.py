import statistics

from collections import defaultdict

from mauve.utils import iter_books


def round_down(num, divisor):
    return num - (num % divisor)


class BaseWordUsage:

    def __init__(self, print_rate=100, required_genre=None, required_lang=None, required_safe_to_use=None):
        self.print_rate = print_rate
        self.groups = defaultdict(dict)
        self.prevs = defaultdict(int)

        self.required_genre = required_genre
        self.required_lang = required_lang
        self.required_safe_to_use = required_safe_to_use

    def grouper(self, book):
        raise NotImplementedError()
        ## Can group by multiple things too
        # return '%s - %s' % (book.author.gender, 25 * round(book.author.birth_year/25)

    def update_groups(self, book):
        counts = book.word_counts
        local_keys = counts.keys()
        tot = len(book.words)

        group_names = self.grouper(book)
        if group_names == []:
            return None

        for group_name in group_names:
            global_keys = self.groups[group_name].keys()
            for s in set(list(global_keys)) - set(list(local_keys)):
                counts[s] = 0
            for k, v in counts.items():
                try:
                    self.groups[group_name][k].append(v / tot)
                except:
                    self.groups[group_name][k] = [0] * self.prevs[group_name] + [v / tot]

            self.prevs[group_name] += 1

    def get_stats(self):
        alt_groups = defaultdict(dict)
        for key in self.groups.keys():
            alt_groups[key] = {
                o[0]: statistics.mean(o[1]) for o in sorted(
                    self.groups[key].items(),
                    key=lambda item: statistics.mean(item[1]),
                    reverse=True
                )
            }

        results = []
        for base_group in alt_groups.keys():
            if base_group is None:
                continue
            for cmp_group in alt_groups.keys():
                if cmp_group is None or cmp_group == base_group:
                    continue

                words_data = {}
                for word in list(alt_groups[base_group].keys()) + list(alt_groups[cmp_group].keys()):
                    words_data[word] = alt_groups[base_group].get(word, 0) - alt_groups[cmp_group].get(word, 0)

                results.append(
                    (
                        cmp_group,
                        base_group,
                        [
                            i[0] for i in sorted(
                                words_data.items(),
                                key=lambda item: item[1]
                            )[:10]
                        ]
                    )
                )
        return results

    def print_stats(self):
        for cmp_group, base_group, data in self.get_stats():
            print(
                '%s < %s: %s' % (
                    base_group,
                    cmp_group,
                    data
                )
            )

    def process(self, print_rate=100):
        for idx, book in enumerate(iter_books()):
            # Maybe only update prev if update_groups did anything.
            # Doesn't really matter
            self.update_groups(book)
            if idx % print_rate == 0:
                self.print_stats()

    def get_is_usable(self, book):
        if not book.has_content:
            return False
        if any([
            self.required_genre and not book.is_genre(self.required_genre),
            self.required_lang and not book.lang == self.required_lang,
            self.required_safe_to_use and not book.safe_to_use
        ]):
            return False
        return True


class AuthorGenderWordUsage(BaseWordUsage):

    def grouper(self, book):
        groups = []
        if self.get_is_usable(book):
            groups.append(book.author.gender)
        return groups


class AuthorNationalityWordUsage(BaseWordUsage):

    def grouper(self, book):
        groups = []
        if self.get_is_usable(book):
            groups.append(book.author.nationality)
        return groups


class AuthorDOBWordUsage(BaseWordUsage):

    def grouper(self, book):
        groups = []
        if self.get_is_usable(book):
            groups.append(round_down(book.author.birth_year, 10))
        return groups


class PublishedYearWordUsage(BaseWordUsage):

    def grouper(self, book):
        groups = []
        if self.get_is_usable(book):
            groups.append(round_down(book.year_published, 10))
        return groups


class GenreWordUsage(BaseWordUsage):

    def grouper(self, book):
        groups = []
        if self.get_is_usable(book):
            groups.extend([t.name for t in book.tags])
        return groups

import statistics

from collections import defaultdict

from mauve.utils import iter_books


class BaseWordUsage:

    def __init__(self, print_rate=100):
        self.print_rate = print_rate
        self.groups = defaultdict(dict)
        self.prev = 0

    def grouper(self, book):
        raise NotImplementedError()
        ## Can group by multiple things too
        # return '%s - %s' % (book.author.gender, 25 * round(book.author.birth_year/25)

    def update_groups(self, book):
        counts = book.word_counts
        local_keys = counts.keys()
        tot = len(book.words)

        group_name = self.grouper(book)
        if group_name is None:
            return None

        global_keys = self.groups[group_name].keys()
        for s in set(list(global_keys)) - set(list(local_keys)):
            counts[s] = 0
        for k, v in counts.items():
            try:
                self.groups[group_name][k].append(v / tot)
            except:
                self.groups[group_name][k] = [0] * self.prev + [v / tot]

    def print_stats(self):
        alt_groups = defaultdict(dict)
        for key in self.groups.keys():
            alt_groups[key] = {
                o[0]: statistics.mean(o[1]) for o in sorted(
                    self.groups[key].items(),
                    key=lambda item: statistics.mean(item[1]),
                    reverse=True
                )
            }

        for base_group in alt_groups.keys():
            if base_group is None:
                continue
            for cmp_group in alt_groups.keys():
                if cmp_group is None or cmp_group == base_group:
                    continue

                data = {}
                for word in list(alt_groups[base_group].keys()) + list(alt_groups[cmp_group].keys()):
                    data[word] = alt_groups[base_group].get(word, 0) - alt_groups[cmp_group].get(word, 0)

                print(
                    '%s > %s: %s' % (
                        cmp_group,
                        base_group,
                        [
                            i[0] for i in sorted(
                                data.items(),
                                key=lambda item: item[1]
                            )[:10]
                        ]
                    )
                )

    def process(self, print_rate=100):
        for idx, book in enumerate(iter_books()):
            # Maybe only update prev if update_groups did anything.
            # Doesn't really matter
            self.update_groups(book)
            self.prev += 1
            if idx % print_rate == 0:
                self.print_stats()


class GenderWordUsage(BaseWordUsage):

    def grouper(self, book):
        if not book.is_genre('fiction') or not book.safe_to_use or not book.has_content or not book.lang == 'en':
            return None

        return book.author.gender


# TODO: by rounded author birth
# TODO: by rounded book published date
# TODO: by genre
# TODO: by nationality

# Interesting to have things not by male / female author but by keeping it within the same decade since words changed a lot over time and men generally wrote earlier books

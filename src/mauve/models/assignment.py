from nltk.corpus import stopwords

from mauve.utils import get_stem, get_lem, lower


class Assignment():

    def __init__(self, sentence, p, n, c, extra):
        self.sentence = sentence
        self.p = p
        self.n = n
        self.c = c
        self.extra = extra

    def serialize(self):
        return {
            'p': self.p.serialize(),
            'n': self.n.serialize(),
            'c': self.c.serialize(),
            'extra': self.extra,
            'sentence': self.sentence.serialize()
        }


def extract_assignments(sentence):
    original_joining_words = ['is', 'are', 'am', 'was', 'were', 'be']
    joining_words = original_joining_words
    assignments = []

    good = False
    for w in joining_words:
        if ' ' + w + ' ' in sentence.text:
            good = True
            break

    if not good:
        return {}

    cleaned_segments = []
    for s in sentence.segments:
        if s.text not in ['so', 'very', 'an', 'a', 'the']:
            cleaned_segments.append(s)

    for idx, (p, c, n) in enumerate(sentence.previous_current_next(cleaned_segments)):

        if not p or not c or not n:
            continue

        if not p.is_wordy or not n.is_wordy:
            continue

        if c.text.lower() in original_joining_words:

            if (not p.is_noun and not p.is_prp) and not p.text in sentence.people:
                continue

            n_text = n.text

            extra = None
            try:
                extra_index = idx + 2

                is_ly = False
                try:
                    is_ly = 'ly' == n_text[-2:]
                except:
                    pass

                if n.text in ['not', 'no', 'a', 'why', 'by', 'quite', 'very', 'well', 'really']:
                    n._text = n._text + ' ' + lower(cleaned_segments[idx + 2].text)
                    extra_index = idx + 3

                try:
                    after_word = lower(cleaned_segments[extra_index].text)
                    if any([
                        n.is_verb or n.is_adj,
                        after_word in ['that', 'about', 'over', 'in', 'about', 'to', 'it', 'by', 'of', 'at', 'its', 'as', 'on', 'a'],
                        is_ly
                    ]):
                        extra = ' '.join([i.text for i in cleaned_segments[extra_index:]]).split(' and ')[0].split(',')[0]
                except:
                    pass

            except Exception as ex:
                print(ex)
                pass

            assignments.append(
                Assignment(
                    sentence,
                    p,
                    n,
                    c,
                    extra
                )
            )

    return assignments

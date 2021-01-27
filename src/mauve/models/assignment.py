from mauve.utils import (
    lower,
    previous_current_next
)


class Assignment():

    def __init__(self, sentence, p, n, c, extra):
        '''

        :param sentence: The full sentence object for some context
        :param p: previous phrase (this)
        :param n: next phrase (silly)
        :param c: current phrase (is)
        :param extra: the text after the next phrase. Not super
        useful, prob goint to remove
        '''
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
    '''
    Given a sentence, pull out the assignments made in the sentence

    :param sentence: Sentence object
    :return:
    '''
    original_joining_words = ['is', 'are', 'am', 'was', 'were', 'be']
    joining_words = original_joining_words
    assignments = []

    good = False
    for joining_word in joining_words:
        if ' ' + joining_word + ' ' in sentence.text:
            good = True
            break

    if not good:
        return []

    cleaned_segments = []
    for s in sentence.segments:
        if s.text not in ['so', 'very', 'an', 'a', 'the']:
            cleaned_segments.append(s)

    for idx, (p, c, n) in enumerate(previous_current_next(cleaned_segments)):

        if any([
            not p, not c, not n,
            not getattr(p, 'is_wordy', None), not getattr(n, 'is_wordy', None)
        ]):
            continue

        if c.text.lower() in original_joining_words:

            if p.text not in sentence.people:
                continue

            ## Including below does all but I just care about personal things
            #if (
            #    not p.is_noun and not p.is_prp
            #) and p.text not in sentence.people:
            #    continue

            n_text = n.text

            extra = None
            try:
                extra_index = idx + 2

                is_ly = False
                try:
                    is_ly = 'ly' == n_text[-2:]
                except:
                    pass

                if n.text in ['not', 'no', 'a', 'why', 'by', 'quite', 'very', 'well', 'really'] or is_ly or n.tag == 'ORDINAL':
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

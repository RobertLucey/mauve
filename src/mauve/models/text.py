from collections import (
    defaultdict,
    Counter
)
import os
import pickle

from cached_property import cached_property

from langdetect import detect as langdetect

import nltk

from mauve.utils import (
    rflatten,
    replace_sub,
    flatten,
    clean_gutenberg,
    split_include,
    get_loose_filepath,
    get_file_content
)
from mauve.utils import (
    quote_aware_sent_tokenize,
    replace_phrases
)
from mauve.names import NAMES
from mauve.constants import (
    BORING_WORDS,
    ENG_WORDS,
    TOKEN_VERSION,
    PROFANITY_LIST,
    SENTENCE_TERMINATORS,
    EXTENDED_PUNCTUATION
)
from mauve.contractions import replace_contractions

from mauve.models.generic import GenericObject
from mauve.models.person import People
from mauve.models.line import Line, Lines

from mauve import (
    VADER,
    Tagger
)

from mauve.models.sentence import Sentence


class TextBody(GenericObject, Tagger):
    """
    A cleaner text body
    Something that holds many sentences / paragraphs relating to one
    piece of writing
    """

    def __init__(self, *args, **kwargs):
        """

        :kwarg content: Text content as a string
        :kwarg content_path: Path to a txt file containing the content
        """
        self._content = kwargs.get('content', None)
        self.content_path = kwargs.get('content_path', None)
        super(TextBody, self).__init__(*args, **kwargs)

    def __del__(self):
        attrs_to_del = [
            'lang',
            'sentences_tokens',
            'sentences',
            'content',
            'dictionary_words',
            'words',
            'all_tokens',
            'word_tokens',
            'raw_content',
            'basic_content',
            'content'
        ]

        for attr in attrs_to_del:
            try:
                delattr(self, attr)
            except:
                pass

    @property
    def lines(self):
        return Lines(data=[
            Line(l, line_no=idx) for idx, l in enumerate(self.content.split('\n'))
        ])

    def get_lexical_diversity(self, only_dictionary_words=False):
        """

        :kwargs only_dictionary_words:
        :return:
        :rtype:
        """
        if only_dictionary_words:
            return float(len(set(self.dictionary_words))) / len(self.dictionary_words)
        return float(len(set(self.words))) / self.word_count

    @property
    def words(self):
        """

        :return:
        :rtype: list
        """
        txt = self.content.translate(
            str.maketrans(
                '',
                '',
                ''.join(['\n', '\n\n'] + EXTENDED_PUNCTUATION)
            )
        )
        return [i for i in txt.split() if i]

    def get_profanity_score(self):
        """
        Return how many instances of profanity were used every 10000 words
        A profane phrase may be many words so not exactly every 10000 words

        :return: How profane the current piece of text is
        :rtype: float
        """
        words = [w.lower() for w in self.words]
        lower_content = self.raw_content.lower()
        included_profanities = []
        for profanity in sorted(PROFANITY_LIST):
            if profanity not in lower_content:
                continue
            words = replace_sub(words, profanity.split(), [profanity])
            if profanity in words:
                included_profanities.append(profanity)

        div = len(words) / 10000.
        return sum([words.count(profanity) for profanity in included_profanities]) / div

    @property
    def has_content(self):
        return self.raw_content != ''

    @cached_property
    def basic_content(self):
        return clean_gutenberg(self.raw_content)

    @cached_property
    def content(self):
        return replace_contractions(self.basic_content)

    @cached_property
    def raw_content(self):
        content = ''
        if self._content is not None:
            content = self._content

        if self.content_path is not None:
            try:
                content = open(
                    self.content_path,
                    'r',
                    encoding='utf8'
                ).read()
            except Exception as ex:
                print('BAD FILE: %s' % (self.content_path))
                print(ex)
        return content

    @cached_property
    def sentiment(self):
        return VADER.polarity_scores([sentence for sentence in self.sentences])

    @cached_property
    def lang(self):
        # TODO: update metadata and use as a cache since this can't be very good
        # Also only go far enough until we're certain. Don't need to process entire books
        try:
            return langdetect(self.raw_content[:50000])
        except Exception:
            return 'unknown'

    @cached_property
    def basic_sentences(self):
        """
        A faster (and worse) way to get sentences of a piece of text
        """
        content = self.basic_content
        for terminator in list(SENTENCE_TERMINATORS) + ['\n']:
            content = content.replace(terminator, terminator + '___mauve_terminator___')
        return content.split('___mauve_terminator___')

    @cached_property
    def sentences(self):
        return nltk.sent_tokenize(self.content)

    @cached_property
    def quote_aware_sentences(self):
        return quote_aware_sent_tokenize(self.content)

    @cached_property
    def phrases_content(self):
        try:
            return replace_phrases(self.content)
        except Exception as ex:
            print('Skipping content: %s' % (ex))

    @cached_property
    def assignments(self):
        content = self.content

        if content is None:
            return []

        return flatten([
            Sentence(s).assignments for s in nltk.tokenize.sent_tokenize(content)
        ])

    @cached_property
    def speech(self):
        """

        :return: list of Speech objects
        """

        speech = {
            line.line_no: line.get_speech() for line in self.lines
        }

        data = []
        build = []
        for line_no, speech_items in speech.items():
            if speech_items == [] and line_no != 0:
                data.append(build)
                build = []
            else:
                if speech_items != []:
                    build.append(speech_items)

        for block in data:
            speakers = []
            for speech_items in block:

                if speech_items[0].speaker.name != '':
                    speakers.append(speech_items[0].speaker)
                else:
                    added = False
                    for speech_item in speech_items:
                        if speech_item.speaker.name == '':
                            # TODO: handle he / she too
                            try:
                                speech_item.speaker = speakers[-2]
                                if not added:
                                    added = True
                                    speakers.append(speakers[-2])
                            except:
                                pass

        return rflatten(list(speech.values()))

    @cached_property
    def people(self):
        """
        Extract all People from text. This is pretty stupid so includes
        a lot of false positives

        :return People
        """
        people = People()
        for sentence in self.sentences:
            for person in Sentence(sentence).people:
                people.append(person)
        return people

    def get_speech_by_people(self, people=None):
        """

        :kwarg people: People object / list of Person objects
                        None to get speech of all people
        :return: dict of list of speech {speaker_name: [speech, speech]}
        """
        if people:
            names = [p.name.lower() for p in people]
        speech_people_map = defaultdict(list)
        for speech in self.speech:
            if speech:
                if people is not None:
                    if speech.speaker.name.lower() in names:
                        speech_people_map[speech.speaker.name].append(speech)
                else:
                    speech_people_map[speech.speaker.name].append(speech)
        return speech_people_map

    def get_assignments_by(self, left_text):
        """
        Get assignments by the thing being assigned to

        :param left_text: whatever is being assigned. left_text is something
        """
        assignments = []
        for assignment in self.assignments:
            if left_text.lower() in assignment[0].text.lower():
                assignments.append(assignment[2].text)
        return assignments

    def get_profanity_by_people(self, people=None):
        speech = self.get_speech_by_people(people=people)
        return {
            person_name: TextBody(
                content=' .'.join([s.text for s in speech_items])
            ).get_profanity_score() for person_name, speech_items in speech.items()
        }

    def get_sentiment_by_people(self, people=None):
        """
        Use vader sentiment to get the sentiment of all a character has said

        :kwarg people: People object / list of Person objects
                        None to get speech of all people
        :return: list of dicts {name: something, sentiment: {pos: 0, neg: 0 , neu: 0, compound: 0}}
        """
        speech = self.get_speech_by_people(people=people)
        return {
            person_name: TextBody(
                content=' .'.join([s.text for s in speech_items])
            ).sentiment for person_name, speech_items in speech.items()
        }

    def count_usage(self, phrase, split_multi=False, nosplit=False):


        """  USE THIS THING
                    texts = split_include(
                        split_include(
                            sentence.split(' '),
                            ','
                        ),
                        '.'
                    )
        """

        if nosplit:
            return self.content.count(phrase)

        if isinstance(phrase, (list, set)):
            if split_multi:
                values = defaultdict(int)
                for word in self.basic_content.split(' '):
                    if word in phrase:
                        values[word] += 1
                return values

            count = 0
            for word in self.basic_content.split(' '):
                if word in phrase:
                    count += 1
            return count
        else:
            if ' ' in phrase:
                return self.basic_content.replace(
                    phrase,
                    phrase.replace(' ', '_')
                ).count(phrase)
            return self.basic_content.split(' ').count(phrase)

    def get_pre_post(self, phrase, simple=False):
        """
        Get the segments pre and post a phrase pair

        :param phrase: str can be a word or many or whatever
        """

        # TODO multi instances in sentence. Don't care enough for the moment

        pairs = defaultdict(list)

        if phrase not in self.basic_content:
            return pairs

        for sentence in self.basic_sentences:
            if phrase in sentence:

                # TODO: make the phrase a segment if multi word

                unsplit_phrase = phrase.replace(' ', '_')

                if simple:
                    texts = split_include(
                        split_include(
                            sentence.split(' '),
                            ','
                        ),
                        '.'
                    )
                else:
                    s = Sentence(sentence.replace(phrase, unsplit_phrase))
                    texts = [i.text.lower() for i in s.segments]
                try:
                    idx = texts.index(unsplit_phrase)

                    pre = texts[idx - 1]
                    if idx == 0:
                        pre = None

                    post = texts[idx + 1]
                    if idx + 1 == len(texts):
                        post = None

                    if pre is not None and pre not in EXTENDED_PUNCTUATION:
                        pairs['pre'].append(pre)

                    if post is not None and post not in EXTENDED_PUNCTUATION:
                        pairs['post'].append(post)
                except (ValueError, IndexError):
                    continue

        return pairs

    @cached_property
    def sentences_tokens(self):
        """

        :return:
        :rtype: list
        """
        size = len(self.all_tokens)
        idx_list = [
            idx + 1 for idx, val in enumerate(self.all_tokens) if val[0] in SENTENCE_TERMINATORS
        ]

        return [
            self.all_tokens[i: j] for i, j in zip(
                [0] + idx_list,
                idx_list + ([size] if idx_list[-1] != size else [])
            )
        ]

    @cached_property
    def all_tokens(self):
        if self.all_tokens_pickle_path is None:
            return self.pos_tag(nltk.word_tokenize(self.content))

        data = []
        if get_loose_filepath(self.all_tokens_pickle_path):
            data = get_file_content(self.all_tokens_pickle_path)
        else:
            data = self.pos_tag(nltk.word_tokenize(self.content))
            try:
                f_pickle = open(self.all_tokens_pickle_path, 'wb')
                pickle.dump(data, f_pickle)
                f_pickle.close()
            except Exception as ex:
                print('Could not open file %s: %s' % (self.all_tokens_pickle_path, ex))

        return data

    @cached_property
    def word_tokens(self):
        """
        """
        # TODO: Get wordtokens from alltokens when care enough

        if self.word_tokens_pickle_path is None:
            return self.pos_tag(self.words)

        data = []
        if get_loose_filepath(self.word_tokens_pickle_path):
            data = get_file_content(get_loose_filepath(
                self.word_tokens_pickle_path)
            )
        else:
            data = self.pos_tag(self.words)
            try:
                f_pickle = open(self.word_tokens_pickle_path, 'wb')
                pickle.dump(data, f_pickle)
                f_pickle.close()
            except Exception as ex:
                print('Could not open file %s: %s' % (self.word_tokens_pickle_path, ex))

        return data

    @property
    def all_tokens_pickle_path(self):
        if self.content_path is None:
            return None
        return self.content_path + '.all_tokenv{}.pickle'.format(TOKEN_VERSION)

    @property
    def word_tokens_pickle_path(self):
        if self.content_path is None:
            return None
        return self.content_path + '.word_tokenv{}.pickle'.format(TOKEN_VERSION)

    @cached_property
    def dictionary_words(self):
        return [
            w for w in self.words if w.lower() in ENG_WORDS and w.isalpha()
        ]

    @property
    def word_count(self):
        """

        :return: the number of individual words in the piece of text
        :rtype: int
        """
        return len(self.words)

    def get_word_counts(self, only_include_words=None):
        """
        Get the counts of dictionary words.

        Usage:
            >>> TextBody(content='Wake me up before you go go!').word_counts()
            {'wake': 1, 'me': 1, 'up': 1, 'before': 1, 'you': 1, 'go': 2}

            >>> TextBody(content='Wake me up before you go go!').word_counts(only_include_words={'up', 'go'})
            {'up': 1, 'go': 2}
        """

        if only_include_words is not None:
            return dict(
                Counter(
                    [
                        w.lower() for w in self.dictionary_words if w.lower() in only_include_words
                    ]
                )
            )

        return dict(
            Counter(
                [
                    w.lower() for w in self.words if all([
                        w.lower() not in BORING_WORDS,
                        w not in NAMES,
                        w.isalpha()
                    ])
                ]
            )
        )

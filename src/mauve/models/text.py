from collections import defaultdict

import statistics

from cached_property import cached_property

import textstat
from langdetect import detect as langdetect

import nltk

from mauve.utils import flatten, clean_gutenberg
from mauve.phrases import replace_phrases
from mauve.utils import quote_aware_sent_tokenize
from mauve.constants import (
    ENG_WORDS,
    PROFANITY_LIST,
    SENTENCE_TERMINATORS,
    SIMPLE_TOKEN_MAP,
    ANALYSIS_VERSION,
    EXTENDED_PUNCTUATION
)
from mauve.contractions import replace_contractions

from mauve.models.generic import GenericObject
from mauve.models.person import People
from mauve.profanity import PROFANITY_TREE
from mauve.bst import (
    create,
    search
)

from mauve import (
    GENDER_DETECTOR,
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
            'adverbs',
            'adjectives',
            'nouns',
            'proper_nouns',
            'verbs',
            'content',
            'dictionary_words',
            'words',
            'tokens'
        ]

        for attr in attrs_to_del:
            try:
                delattr(self, attr)
            except:
                pass

    def get_lexical_diversity(self, only_dictionary_words=False):
        """

        :kwargs only_dictionary_words:
        :return:
        :rtype:
        """
        if only_dictionary_words:
            return float(len(set(self.dictionary_words))) / len(self.dictionary_words)
        return float(len(set(self.words))) / len(self.words)

    @property
    def words(self):
        """

        :return:
        :rtype: list
        """
        return [w for w in nltk.word_tokenize(self.content) if w not in EXTENDED_PUNCTUATION]

    def get_profanity_score(self):
        """
        Return how many instances of profanity were used every 10000 words
        A profane phrase may be many words so not exactly every 10000 words

        :return: How profane the current piece of text is
        :rtype: float
        """
        word_counts = {}
        profane_words = []

        content = self.content
        for p in PROFANITY_LIST:
            content = content.replace(p, p.replace(' ', '_'))

        words = [w for w in nltk.word_tokenize(content) if w not in EXTENDED_PUNCTUATION]

        original_len = len(words)

        lower_words = [i.lower().replace('_', ' ') for i in words]

        tree = PROFANITY_TREE
        for word in lower_words:
            if search(tree, word) != (0, 0):
                profane_words.append(word)

        for word in profane_words:
            word_counts[word.lower()] = lower_words.count(word.lower())

        if not profane_words:
            return 0

        div = original_len / 10000.
        return sum(word_counts.values()) / div

    def set_content_location(self, content_path):
        """

        :param content_path:
        """
        self.content_path = content_path

    @property
    def basic_content(self):
        content = ''
        if self._content is not None:
            content = self._content

        if self.content_path is not None:
            try:
                content = open(
                    self.content_path,
                    'r',
                    encoding='latin1'
                ).read()
            except Exception as ex:
                print('BAD FILE: %s' % (self.content_path))
                print(ex)
                content = ''

        if 'PROJECT GUTENBERG EBOOK' in content:
            content = clean_gutenberg(content)

        return content

    @property
    def content(self):
        content = ''
        if self._content is not None:
            content = self._content

        if self.content_path is not None:
            try:
                content = open(
                    self.content_path,
                    'r',
                    encoding='latin1'
                ).read()
            except Exception as ex:
                print('BAD FILE: %s' % (self.content_path))
                print(ex)
                content = ''

        if 'PROJECT GUTENBERG EBOOK' in content:
            content = clean_gutenberg(content)

        return replace_contractions(content)

    @cached_property
    def sentiment(self):
        # Need more power but this may be an indication
        return VADER.polarity_scores([a for a in self.sentences])

    @cached_property
    def lang(self):
        # TODO: update metadata and use as a cache since this can't be very good
        # Also only go far enough until we're certain. Don't need to process entire books
        return langdetect(self.content)

    @cached_property
    def basic_sentences(self):
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
        content = self.content

        if content is None:
            return []

        return flatten([
            Sentence(s).speech for s in quote_aware_sent_tokenize(content)
        ])

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
            person_name: TextBody(content=' .'.join([s.text for s in speech_items])).sentiment for person_name, speech_items in speech.items()
        }

    def count_phrase_usage(self, phrase):

        if isinstance(phrase, (list, set)):
            count = 0
            for word in self.basic_content.split(' '):
                if word in phrase:
                    print(word)
                    count += 1
            return count
        else:

            if ' ' in phrase:
                return self.basic_content.replace(phrase, phrase.replace(' ', '_')).count(phrase)
            else:
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
                    texts = sentence.split(' ')
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
        size = len(self.tokens)
        idx_list = [
            idx + 1 for idx, val in enumerate(self.tokens) if val[0] in SENTENCE_TERMINATORS
        ]

        return [
            self.tokens[i: j] for i, j in zip(
                [0] + idx_list,
                idx_list + ([size] if idx_list[-1] != size else [])
            )
        ]

    @property
    def word_count(self):
        """

        :return: the number of individual words in the piece of text
        :rtype: int
        """
        return len(self.words)

from collections import Counter
from collections import defaultdict

import statistics

from cached_property import cached_property

import textstat
from langdetect import detect as langdetect

import nltk

from mauve.utils import flatten
from mauve.phrases import replace_phrases
from mauve.utils import quote_aware_sent_tokenize
from mauve.constants import (
    ENG_WORDS,
    PROFANITY_LIST,
    SENTENCE_TERMINATORS,
    SIMPLE_TOKEN_MAP,
    ANALYSIS_VERSION
)

from mauve.models.generic import GenericObject
from mauve.models.person import People
from mauve.bst import (
    create,
    search
)

from mauve.splunk_push import StreamSubmit

from mauve import (
    GENDER_DETECTOR,
    VADER,
    Tagger
)

from mauve.models.sentence import Sentence


class Text(GenericObject, Tagger):

    def __init__(self, *args, **kwargs):
        self.content_path = kwargs.get('content_path', None)
        super(Text, self).__init__(*args, **kwargs)

    @cached_property
    def content(self):
        """
        """
        try:
            return open(
                self.content_path,
                'r',
                encoding='latin1'
            ).read()
        except Exception as ex:
            print('BAD FILE: %s' % (self.content_path))
            print(ex)
            return ''

    def set_content_location(self, content_path):
        """

        :param content_path:
        """
        self.content_path = content_path

    def get_top_adjectives(self, num_to_get):
        adjs = Counter(
            [a.lower() for a in self.adjectives]
        ).most_common(num_to_get * 2)
        return dict(
            [
                a for a in adjs if all([
                a[0] in self.dictionary_words,
                'â' not in str(a),
                a != 'n'
            ])
            ][0:num_to_get]
        )

    def get_top_nouns(self, num_to_get):
        nouns = Counter(
            [a.lower() for a in self.nouns]
        ).most_common(num_to_get * 2)
        return dict(
            [
                a for a in nouns if all([
                a[0] in self.dictionary_words,
                'â' not in str(a),
                a != 'n'
            ])
            ][0:num_to_get]
        )

    def get_top_verbs(self, num_to_get):
        verbs = Counter(
            [a.lower() for a in self.verbs]
        ).most_common(num_to_get * 2)
        return dict(
            [
                a for a in verbs if all([
                a[0] in self.dictionary_words,
                'â' not in str(a),
                a != 'n'
            ])
            ][0:num_to_get]
        )

    def get_profanity_score(self):
        word_counts = {}
        words = []

        original_len = len(self.words)

        tree = create(self.words)
        for curse in PROFANITY_LIST:
            if search(tree, curse) != (0, 0):
                words.append(curse)

        for word in words:
            word_counts[word] = self.words.count(word)

        if words == []:
            return 0

        div = original_len / 10000.
        return sum(word_counts.values()) / div

    def get_token_type_score(self, token_type):
        assert (token_type in SIMPLE_TOKEN_MAP.values())
        div = len(self.words) / 10000.
        return len([m for m in self.tokens if SIMPLE_TOKEN_MAP[m[1]] == token_type]) / div

    def get_lexical_diversity(self, only_dictionary_words=False):
        '''

        :kwargs only_dictionary_words:
        :return:
        :rtype:
        '''
        if only_dictionary_words:
            return float(len(set(self.dictionary_words))) / len(self.dictionary_words)
        return float(len(set(self.words))) / len(self.words)

    def get_avg_word_len(self, only_dictionary_words=False):
        '''

        :kwargs only_dictionary_words:
        :return:
        :rtype:
        '''
        if only_dictionary_words:
            return statistics.mean([len(i) for i in self.dictionary_words])
        return statistics.mean([len(i) for i in self.words])

    def get_avg_sentence_word_len(self):
        return statistics.mean(
            [len(nltk.word_tokenize(i)) for i in self.sentences]
        )

    def get_avg_sentence_char_len(self):
        return statistics.mean(
            [len(i) for i in self.sentences]
        )

    def push_to_splunk(self):
        StreamSubmit().submit(
            'books',
            self.serialize(),
            source=self.source,
            sourcetype=self.sourcetype
        )

    @cached_property
    def sentiment(self):
        return VADER.polarity_scores(
            [
                a for a in self.sentences
            ]
        )  # Need more power but this may be an indication

    def serialize_stats(self):
        return {
            'analysis_version': int(ANALYSIS_VERSION),
            'author': getattr(self, 'author', None),
            'author_gender': self.author_gender,
            'word_count': len(self.words),
            'lexical_diversity': self.get_lexical_diversity(),
            'avg_word_len': self.get_avg_word_len(),
            'profanity_score': self.get_profanity_score(),
            'avg_sentence_word_len': self.get_avg_sentence_word_len(),
            'avg_sentence_char_len': self.get_avg_sentence_char_len(),
            'adverb_score': self.get_token_type_score('adverb'),
            'interjection_score': self.get_token_type_score('interjection'),
            'adjective_score': self.get_token_type_score('adjective'),
            'top_adjectives': self.get_top_adjectives(10),
            'top_nouns': self.get_top_nouns(10),
            'top_verbs': self.get_top_verbs(10),
            'flesch_reading_ease_score': textstat.flesch_reading_ease(
                self.content
            ),
            'crawford_score': textstat.crawford(self.content),
            'vader_pos': self.sentiment['pos'],
            'vader_neg': self.sentiment['neg'],
            'vader_neu': self.sentiment['neu'],
            'vader_compound': self.sentiment['compound'],
        }

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
            'author_gender',
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

    @cached_property
    def lang(self):
        # TODO: update metadata and use as a cache since this can't be
        # very good
        # Also only go far enough until we're certain. Don't need to
        # process entire books
        return langdetect(self.content)

    @cached_property
    def sentences_tokens(self):
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

    @cached_property
    def sentences(self):
        return nltk.tokenize.sent_tokenize(self.content)

    @cached_property
    def adverbs(self):
        return [m[0] for m in self.tokens if SIMPLE_TOKEN_MAP[m[1]] == 'adverb']

    @cached_property
    def adjectives(self):
        return [m[0] for m in self.tokens if SIMPLE_TOKEN_MAP[m[1]] == 'adjective']

    @cached_property
    def nouns(self):
        return [m[0] for m in self.tokens if SIMPLE_TOKEN_MAP[m[1]] == 'noun']

    @cached_property
    def proper_nouns(self):
        return [m[0] for m in self.tokens if SIMPLE_TOKEN_MAP[m[1]] == 'proper noun']

    @cached_property
    def verbs(self):
        return [m[0] for m in self.tokens if SIMPLE_TOKEN_MAP[m[1]] == 'verb']

    @cached_property
    def author_gender(self):
        gender = None
        try:
            author_split = self.author.split(' ')
        except:
            return
        else:
            if '.' in author_split[0]:
                # Try use the author's wikipedia page or something
                pass
            elif ' and ' in self.author.lower() or '&' in self.author.lower():
                pass
            else:
                gender = GENDER_DETECTOR.get_gender(author_split[0])
                if gender != 'male' and gender != 'female':
                    # Try use the author's wikipedia page or something
                    gender = None

        return gender

    @cached_property
    def dictionary_words(self):
        return [
            w.lower() for w in self.words if w.lower() in ENG_WORDS and w.isalpha()
        ]

    @cached_property
    def words(self):
        raise NotImplementedError()

    @cached_property
    def tokens(self):
        raise NotImplementedError()

    @property
    def reading_age(self):
        raise NotImplementedError()

    @property
    def word_count(self):
        return len(self.words)

    @cached_property
    def phrases_content(self):
        try:
            return replace_phrases(self.content)
        except Exception as ex:
            print('Skipping content: %s' % (ex))

    @property
    def assignments(self):
        content = self.content

        if content is None:
            return []

        return [
            Sentence(s).assignments for s in nltk.tokenize.sent_tokenize(content)
        ]

    @property
    def speech(self):
        content = self.content

        if content is None:
            return []

        return [
            Sentence(s).speech for s in quote_aware_sent_tokenize(content)
        ]


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
            'author_gender',
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

    def get_profanity_score(self):
        word_counts = {}
        words = []

        original_len = len(self.words)

        tree = create(self.words)
        for curse in PROFANITY_LIST:
            if search(tree, curse) != (0, 0):
                words.append(curse)

        for word in words:
            word_counts[word] = self.words.count(word)

        if not words:
            return 0

        div = original_len / 10000.
        return sum(word_counts.values()) / div

    def set_content_location(self, content_path):
        """

        :param content_path:
        """
        self.content_path = content_path

    @property
    def content(self):
        if self._content is not None:
            return self._content

        if self.content_path is not None:
            try:
                return open(
                    self.content_path,
                    'r',
                    encoding='latin1'
                ).read()
            except Exception as ex:
                print('BAD FILE: %s' % (self.content_path))
                print(ex)
                return ''

        return

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
    def sentences(self):
        return nltk.tokenize.sent_tokenize(self.content)

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

        return [
            Sentence(s).assignments for s in nltk.tokenize.sent_tokenize(content)
        ]

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

        :return People
        """
        people = People()
        for sentence in self.sentences:
            for person in Sentence(sentence).people:
                if person not in people:
                    people.append(person)
        return people

    def get_speech_by_person(self, person):
        """

        :param person: Person object to get where they are the speaker
        :return: List of speech objects
        """
        return [
            s for s in self.speech if s and s.speaker.name.lower() == person.name.lower()
        ]

    def get_assignments_by(self, left_text):
        """
        Get assignments by the thing being assigned to

        :param left_text: whatever is being assigned. left_text is something
        """
        assignments = []
        for sentence_assignments in self.assignments:
            for assignment in sentence_assignments:
                if left_text in assignment[0].text.lower():
                    assignments.append(assignment[2].text)
        return assignments

    def get_speech_by_person(self, people=None):
        if people:
            names = [p.name.lower() for p in people]
        speech_people_map = defaultdict(list)
        for speech in self.speech:
            if speech:
                if people is not None:
                    if speech.speaker.name.lower() in names:
                        speech_people_map[speech.speaker.name].append(speech.text)
                else:
                    speech_people_map[speech.speaker.name].append(speech.text)
        return speech_people_map

    def get_sentiment_by_person(self, people=None):
        speech = self.get_speech_by_person(people=people)
        return [
            {
                'name': person_name,
                'sentiment': TextBody(content=' .'.join(lines)).sentiment
            } for person_name, lines in speech.items()
        ]

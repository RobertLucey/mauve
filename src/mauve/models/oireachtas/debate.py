from collections import defaultdict
import fast_json
import os
import pickle
import requests

from cached_property import cached_property
import bs4
import nltk

from mauve.utils import get_file_content
from mauve.constants import OIREACHTAS_DIR
from mauve.models.text import TextBody


def merge_paras(paras):
    '''
    When you don't care about context it's often easier to treat many
    paragraphs as one.

    :param paras:
    :return: A Para object that just merges all the paras you give it into one.
    '''
    return Para(content='\n\n'.join([m.content for m in paras]))


class Para(TextBody):
    '''
    Paragraph object, has a title, id, and content.

    Inherits from Text which has all the text analysis bits
    '''

    def __init__(self, *args, **kwargs):
        '''

        :kwarg title: Sometimes a paragraph has a title, not often
        :kwarg eid: Incremented id of the paragraph
        :kwarg content: The str text content
        '''
        self.title = kwargs.get('title', None)
        self.eid = kwargs.get('eid', None)

        self.source = 'oireachtas'
        self.sourcetype = 'debate'
        super(Para, self).__init__(*args, **kwargs)

    @cached_property
    def words(self):
        '''

        :return: A list of nltk tokenized words
        '''
        return nltk.word_tokenize(self.content)

    @cached_property
    def tokens(self):
        '''

        :reuturn: A list of nltk tokenized words with their tag
        '''
        return self.pos_tag(self.words)

    def serialize(self):
        return {
            'title': self.title,
            'eid': self.eid,
            'content': self.content,
            'word_count': self.word_count
        }


class Speech():

    def __init__(self, by=None, _as=None, eid=None, paras=None):
        '''

        :kwarg by: The name / identifier of the speaker
        :kwarg _as: The title / position of the speaker
        :kwarf eid: incrementing id of the speech
        :kwarg paras: list of Para objects
        '''
        self.by = by
        self._as = _as
        self.eid = eid

        if paras is not None and paras is not []:
            types = list(set([type(p) for p in paras]))
            assert(len(types) == 1)
            assert(types[0] == Para)

        self.paras = paras if paras else []

    def serialize(self):
        return {
            'by': self.by,
            'as': self._as,
            'eid': self.eid,
            'paras': [p.serialize() for p in self.paras]
        }


class DebateSection():

    def __init__(
        self,
        bill=None,
        contains_debate=None,
        counts=None,
        debate_section_id=None,
        debate_type=None,
        data=None,
        parent_debate_section=None,
        show_as=None,
        speakers=None,
    ):
        self.bill = bill
        self.contains_debate = contains_debate
        self.counts = counts
        self.debate_section_id = debate_section_id
        self.debate_type = debate_type
        self.data = data
        self.parent_debate_section = parent_debate_section
        self.show_as = show_as
        self.speakers = speakers

        self._data = None

    @cached_property
    def speeches(self):
        if self.data is None:
            return

        soup = bs4.BeautifulSoup(self.data, 'html.parser')

        # heading
        # soup.find('debatesection').find('heading').text

        speeches = []

        for speech in soup.find('debatesection').find_all('speech'):
            paras = [
                Para(
                    title=p.attrs.get('title', None),
                    eid=p.attrs.get('eid', None),
                    content=p.text
                ) for p in speech.find_all('p')
            ]

            speeches.append(
                Speech(
                    by=speech.attrs.get('by'),
                    _as=speech.attrs.get('as'),
                    eid=speech.attrs.get('eid'),
                    paras=paras
                )
            )
        return speeches

    def serialize(self):
        return {
            'bill': self.bill,
            'contains_debate': self.contains_debate,
            'counts': self.counts,
            'debate_section_id': self.debate_section_id,
            'debate_type': self.debate_type,
            'parent_debate_section': self.parent_debate_section,
            'show_as': self.show_as,
            'speakers': self.speakers,
            'speeches': [s.serialize() for s in self.speeches]
        }

    @property
    def is_from_pdf(self):
        return self.debate_type is None


class Debate():

    def __init__(self, file_path=None):
        # TODO: also accept being given the data
        self.file_path = file_path

        if not os.path.exists(self.file_path):
            raise Exception()

        for section in self.data['debateRecord']['debateSections']:
            raw_debate_section = section['debateSection']
            self.debate_sections.append(
                DebateSection(
                    bill=raw_debate_section['bill'],
                    contains_debate=raw_debate_section['containsDebate'],
                    counts=raw_debate_section['counts'],
                    debate_section_id=raw_debate_section['debateSectionId'],
                    debate_type=raw_debate_section['debateType'],
                    data=raw_debate_section['data'],
                    parent_debate_section=raw_debate_section['parentDebateSection'],
                    show_as=raw_debate_section['showAs'],
                    speakers=raw_debate_section['speakers']
                )
            )

        # self.download_pdf()

    @property
    def date(self):
        return self.data['contextDate']

    @property
    def chamber(self):
        return self.data['debateRecord']['chamber']['showAs']

    @property
    def counts(self):
        return self.data['debateRecord']['counts']

    @property
    def debate_type(self):
        return self.data['debateRecord']['debateType']

    @cached_property
    def data(self):
        return fast_json.loads(open(self.file_path).read())

    def download_pdf(self):
        chamber = {
            'Dáil Éireann': 'dail',
            'Seanad Éireann': 'seanad'
        }
        url = 'https://data.oireachtas.ie/ie/oireachtas/debateRecord/%s/%s/debate/mul@/main.pdf' % (
            chamber,
            self.date
        )
        pdf_request = requests.get(url, stream=True)
        with open(self.pickle_location.replace('pickle', 'pdf'), 'wb') as pdfile:
            for chunk in pdf_request.iter_content(2000):
                pdfile.write(chunk)

    def serialize(self):
        return {
            'date': self.date,
            'chamber': self.chamber,
            'counts': self.counts,
            'debate_type': self.debate_type,
            'sections': [
                s.serialize() for s in self.debate_sections
            ]
        }

    @property
    def content_by_speaker(self):
        speakers = defaultdict(list)
        for section in self.debate_sections:
            for speech in section.speeches:
                speakers[speech.by].extend(speech.paras)
        return speakers

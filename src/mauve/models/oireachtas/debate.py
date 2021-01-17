from collections import defaultdict
from urllib.request import urlopen
from urllib.request import HTTPError
import os
import pickle
import requests

from cached_property import cached_property
import nltk
import bs4

from mauve.utils import get_file_content
from mauve.constants import OIREACHTAS_DIR
from mauve.models.text import Text


def merge_paras(paras):
    '''
    When you don't care about context it's often easier to treat many
    paragraphs as one.

    :param paras:
    :return: A Para object that just merges all the paras you give it into one.
    '''
    return Para(content='\n\n'.join([m.content for m in paras]))


class Para(Text):
    '''
    Paragraph object, has a title, id, and content.

    Inherits from Text which has all the text analysis bits
    '''

    def __init__(self, title=None, eid=None, content=None):
        '''

        :kwarg title: Sometimes a paragraph has a title, not often
        :kwarg eid: Incremented id of the paragraph
        :kwarg content: The str text content
        '''
        self.title = title
        self.eid = eid
        self.content = content
        super(Para, self).__init__()

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
            'content': self.content
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
            assert(isinstance(types[0], Para))

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
        data_uri=None,
        parent_debate_section=None,
        show_as=None,
        speakers=None,
        speeches=None
    ):
        self.bill = bill
        self.contains_debate = contains_debate
        self.counts = counts
        self.debate_section_id = debate_section_id
        self.debate_type = debate_type
        self.data_uri = data_uri
        self.parent_debate_section = parent_debate_section
        self.show_as = show_as
        self.speakers = speakers
        self.speeches = speeches if speeches else []

        self._data = None
        self.loaded = False

    def load_data(self):
        '''
        Load data from the data_uri to populate the speeches and
        their paragraphs
        '''
        if self.loaded:
            return

        try:
            source = urlopen(self.data_uri)
        except Exception as ex:
            if str(ex) != 'HTTP Error 403: Forbidden':
                raise ex
            return

        soup = bs4.BeautifulSoup(source, 'html.parser')

        # heading
        # soup.find('debatesection').find('heading').text

        for speech in soup.find('debatesection').find_all('speech'):
            paras = [
                Para(
                    title=p.attrs.get('title', None),
                    eid=p.attrs.get('eid', None),
                    content=p.text
                ) for p in speech.find_all('p')
            ]

            self.speeches.append(
                Speech(
                    by=speech.attrs.get('by'),
                    _as=speech.attrs.get('as'),
                    eid=speech.attrs.get('eid'),
                    paras=paras
                )
            )

        # Could also get summary

        self.loaded = True

    def serialize(self):
        return {
            'bill': self.bill,
            'contains_debate': self.contains_debate,
            'counts': self.counts,
            'debate_section_id': self.debate_section_id,
            'debate_type': self.debate_type,
            'data_uri': self.data_uri,
            'parent_debate_section': self.parent_debate_section,
            'show_as': self.show_as,
            'speakers': self.speakers,
            'speeches': [s.serialize() for s in self.speeches]
        }

    @property
    def is_from_pdf(self):
        return self.debate_type is None


class Debate():

    def __init__(
        self,
        date=None,
        chamber=None,
        counts=None,
        debate_sections=None,
        debate_type=None,
        data_uri=None
    ):
        '''

        :kwarg date: The date of the debate in YYYY-MM-DD format
        :kwarg chamber: Dail or Seanad
        :kwarg counts:
        :kwarg debate_sections: list of debate sections in json from the api
        :kwarg debate_type: the tye of the debate, usually just 'debate'
        :kwarg data_uri:
        '''
        self.date = date
        self.chamber = chamber
        self.counts = counts
        self.debate_sections = debate_sections
        self.debate_type = debate_type
        self.data_uri = data_uri

        self.loaded = False

    def load_data(self):
        '''
        Load data from the data_uri to populate the debate sections
        '''
        if self.loaded:
            return

        if os.path.exists(self.pickle_location):
            data = get_file_content(self.pickle_location)
            self.date = data.date
            self.chamber = data.chamber
            self.counts = data.counts
            self.debate_sections = data.debate_sections
            self.debate_type = data.debate_type
            self.data_uri = data.data_uri
        else:
            debate_sections = []
            for section in self.debate_sections:
                raw_debate_section = section['debateSection']
                debate_section = DebateSection(
                    bill=raw_debate_section['bill'],
                    contains_debate=raw_debate_section['containsDebate'],
                    counts=raw_debate_section['counts'],
                    debate_section_id=raw_debate_section['debateSectionId'],
                    debate_type=raw_debate_section['debateType'],
                    data_uri=raw_debate_section['formats']['xml']['uri'],
                    parent_debate_section=raw_debate_section['parentDebateSection'],
                    show_as=raw_debate_section['showAs'],
                    speakers=raw_debate_section['speakers']
                )
                debate_section.load_data()
                debate_sections.append(debate_section)

            self.debate_sections = debate_sections

            chamber = {
                'Dáil Éireann': 'dail',
                'Seanad Éireann': 'seanad'
            }
            url = 'https://data.oireachtas.ie/ie/oireachtas/debateRecord/%s/%s/debate/mul@/main.pdf' % (
                chamber,
                self.date
            )

            pdf_request = requests.get(url, stream=True)

            with open(self.pickle_location.replace('pickle', 'pdf'), 'wb') as fd:
                for chunk in pdf_request.iter_content(2000):
                    fd.write(chunk)

        self.loaded = True


    def serialize(self):
        return {
            'date': self.date,
            'chamber': self.chamber,
            'counts': self.counts,
            'debate_type': self.debate_type,
            'data_uri': self.data_uri,
            'sections': [
                s.serialize() for s in self.debate_sections
            ]
        }

    def write(self):
        f_pickle = open(self.pickle_location, 'wb')
        pickle.dump(self, f_pickle)
        f_pickle.close()

    @property
    def pickle_location(self):
        return os.path.join(
            OIREACHTAS_DIR,
            '%s_%s_%s.pickle' % ('debate', self.chamber, self.date)
        )

    @property
    def content_by_speaker(self):
        speakers = defaultdict(list)
        for section in self.debate_sections:
            for speech in section.speeches:
                speakers[speech.by].extend(speech.paras)
        return speakers

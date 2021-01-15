import os
import json
import pickle
import requests
from collections import defaultdict
from urllib.request import urlopen
from urllib.request import HTTPError

from cached_property import cached_property
import nltk

from mauve.utils import get_file_content
from mauve.constants import OIREACHTAS_DIR
from mauve.models.text import Text

import bs4


def merge_paras(paras):
    return Para(content='\n\n'.join([m.content for m in paras]))



class Para(Text):

    def __init__(self, title=None, eid=None, content=None):
        self.title = title
        self.eid = eid
        self.content = content
        super(Para, self).__init__()

    @cached_property
    def words(self):
        return nltk.word_tokenize(self.content)

    @cached_property
    def tokens(self):
        return nltk.pos_tag(self.words)

    def serialize(self):
        return {
            'title': self.title,
            'eid': self.eid,
            'content': self.content
        }

class Speech():

    def __init__(self, by=None, _as=None, eid=None, paras=None):
        self.by = by
        self._as = _as
        self.eid = eid
        self.paras = paras

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

        # speech

        
        for speech in soup.find('debatesection').find_all('speech'):
            paras = []
            for p in speech.find_all('p'):
                paras.append(
                    Para(
                        title=p.attrs.get('title', None),
                        eid=p.attrs.get('eid', None),
                        content=p.text
                    )
                )

            s = Speech(
                by=speech.attrs.get('by'),
                _as=speech.attrs.get('as'),
                eid=speech.attrs.get('eid'),
                paras=paras
            )
            self.speeches.append(s)

        # for para
        # 'attrs': {'by': '#FrankFahy', 'as': '#Ceann_Comhairle', 'eid': 'spk_1'}

        # could also get summary


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
        return self.debate_type == None


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
        self.date = date
        self.chamber = chamber
        self.counts = counts
        self.debate_sections = debate_sections
        self.debate_type = debate_type
        self.data_uri = data_uri

        self.loaded = False

    def load_data(self):
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
                section = section['debateSection']
                s = DebateSection(
                    bill=section['bill'],
                    contains_debate=section['containsDebate'],
                    counts=section['counts'],
                    debate_section_id=section['debateSectionId'],
                    debate_type=section['debateType'],
                    data_uri=section['formats']['xml']['uri'],
                    parent_debate_section=section['parentDebateSection'],
                    show_as=section['showAs'],
                    speakers=section['speakers']
                )
                s.load_data()
                debate_sections.append(s)

            self.debate_sections = debate_sections


            if self.chamber == 'Dáil Éireann':
                url = 'https://data.oireachtas.ie/ie/oireachtas/debateRecord/dail/%s/debate/mul@/main.pdf' % (self.date)
            else:
                url = 'https://data.oireachtas.ie/ie/oireachtas/debateRecord/seanad/%s/debate/mul@/main.pdf' % (self.date)

            r = requests.get(url, stream=True)
            
            with open(self.pickle_location.replace('pickle', 'pdf'), 'wb') as fd:
                for chunk in r.iter_content(2000):
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
        return os.path.join(OIREACHTAS_DIR, '%s_%s_%s.pickle' % ('debate', self.chamber, self.date))

    @property
    def content_by_speaker(self):
        speakers = defaultdict(list)
        for section in self.debate_sections:
            for speech in section.speeches:
                speakers[speech.by].extend(speech.paras)
        return speakers

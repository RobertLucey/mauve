from unittest import TestCase
import mock

import glob
import os

from mauve.models.oireachtas.debate import (
    merge_paras,
    Para,
    Speech,
    DebateSection,
    Debate
)


class TestDebate(TestCase):

    def test_merge_paras(self):
        para1 = Para(title='title one', content='one one one')
        para2 = Para(title='title two', content='two two two')
        merged_para = merge_paras([para1, para2])
        self.assertEqual(merged_para.content, 'one one one\n\ntwo two two')

    def test_para_words(self):
        para1 = Para(title='title one', content='one one one')
        self.assertEqual(para1.words, ['one', 'one', 'one'])

    def test_para_tokens(self):
        para1 = Para(title='title one', content='one one one')
        self.assertEqual(para1.tokens, [('one', 'CD'), ('one', 'CD'), ('one', 'NN')])

    def test_para_serialize(self):
        para1 = Para(title='title one', content='one one one')
        self.assertEqual(
            para1.serialize(),
            {
                'title': 'title one',
                'eid': None,
                'content': 'one one one'
            }
        )

    def test_speech_serialize(self):
        speech = Speech(
            by='byebye',
            _as='assomething',
            eid='123',
            paras=[
                Para(title='title one', content='one one one')
            ]
        )

        self.assertEqual(
            speech.serialize(),
            {
                'by': 'byebye',
                'as': 'assomething',
                'eid': '123',
                'paras': [
                    {
                        'content': 'one one one',
                        'eid': None,
                        'title': 'title one'
                    }
                ]
            }
        )

    def test_debate_section_load_data(self):
        pass

    def test_debate_section_serialize(self):
        pass

    def test_debate_load_data(self):
        pass

    def test_debate_serialize(self):
        pass

    def test_debate_write(self):
        pass

    def test_debate_pickle_location(self):
        pass

    def test_debate_content_by_speaker(self):
        pass

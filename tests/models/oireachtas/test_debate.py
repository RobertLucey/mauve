from unittest import TestCase

from mauve.models.oireachtas.utils import merge_paras
from mauve.models.oireachtas.debate import (
    Para,
    Speech
)


class TestDebate(TestCase):

    def test_merge_paras(self):
        para1 = Para(title='title one', content='one one one')
        para2 = Para(title='title two', content='two two two')
        merged_para = merge_paras([para1, para2])
        self.assertEqual(merged_para.content, '111\n\n222')

    def test_para_words(self):
        para1 = Para(title='title one', content='one one one')
        self.assertEqual(para1.words, ['111'])

    def test_para_tokens(self):
        para1 = Para(title='title one', content='111')
        self.assertEqual(para1.tokens, [('111', 'CD')])

    def test_para_serialize(self):
        para1 = Para(title='title one', content='111')
        self.assertEqual(
            para1.serialize(),
            {
                'title': 'title one',
                'eid': None,
                'content': '111',
                'word_count': 1
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
                'by': {'gender': None, 'name': 'byebye', 'role': None},
                'as': 'assomething',
                'eid': '123',
                'paras': [
                    {
                        'content': '111',
                        'eid': None,
                        'title': 'title one',
                        'word_count': 1
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


    #def test_assignments(self):
    #    #p = Para(title=None, eid=None, content='I believe Mr. Flynn is a tit. He is tit')
    #    #self.assertEqual(
    #    #    dict(p.assignments),
    #    #    [
    #    #        {
    #    #            'left': 'mr Flynn',
    #    #            'right': 'tit',
    #    #            'extra': None
    #    #        },
    #    #        {
    #    #            'left': 'he',
    #    #            'right': 'tit',
    #    #            'extra': None
    #    #        }
    #    #    ]
    #    #)

    #    p = Para(title=None, eid=None, content='The minister for finance is a tit')
    #    assignments = p.assignments
    #    self.assertEqual(len(assignments), 1)
    #    self.assertEqual(len(assignments[0]), 1)
    #    self.assertEqual(assignments[0][0].p.text, 'minister for finance')
    #    self.assertEqual(assignments[0][0].n.text, 'tit')
    #    self.assertEqual(assignments[0][0].c.text, 'is')
    #    self.assertEqual(assignments[0][0].extra, None)
    #    self.assertEqual(assignments[0][0].sentence.text, 'The minister_for_finance is a tit')

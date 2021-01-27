from unittest import TestCase
import mock

import glob
import os

from mauve.models.text import Sentence, Segment
from mauve.models.books.book import Book
from mauve.models.books.review import Reviews, Review
from mauve.models.books.tag import Tags, Tag
from mauve import constants

from mauve.models.synonym import Synonym


class TestSentence(TestCase):


    # Differentiate between 'that will be done' and 'that has been done'

    def test_get_assignments_ordinal_carry_on(self):

        s = Sentence('currently, Robert is the first person to shove a golf ball up their nose')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0].p.text, 'Robert')
        self.assertEqual(assignments[0].n.text, 'the first person to shove a golf___ball up their nose')
        self.assertEqual(assignments[0].c.text, 'is')
        self.assertEqual(assignments[0].sentence.text, 'currently , Robert is the first person to shove a golf ball up their nose')

    def test_get_assignments(self):

        s = Sentence('Tom Jones is happy')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0].p.text, 'Tom Jones')
        self.assertEqual(assignments[0].n.text, 'happy')
        self.assertEqual(assignments[0].c.text, 'is')
        self.assertEqual(assignments[0].sentence.text, 'Tom_Jones is happy')

        s = Sentence('Tom Jones is happy about it')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0].p.text, 'Tom Jones')
        self.assertEqual(assignments[0].n.text, 'happy about it')
        self.assertEqual(assignments[0].c.text, 'is')
        self.assertEqual(assignments[0].sentence.text, 'Tom_Jones is happy about it')

        s = Sentence('Robert are fun')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0].p.text, 'Robert')
        self.assertEqual(assignments[0].n.text, 'fun')
        self.assertEqual(assignments[0].c.text, 'are')
        self.assertEqual(assignments[0].sentence.text, 'Robert are fun')

        s = Sentence('Robert are not fun')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0].p.text, 'Robert')
        self.assertEqual(assignments[0].n.text, 'not fun')
        self.assertEqual(assignments[0].c.text, 'are')
        self.assertEqual(assignments[0].sentence.text, 'Robert are not fun')

        s = Sentence('Peter is a spider on my shoe')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0].p.text, 'Peter')
        self.assertEqual(assignments[0].n.text, 'a spider on my shoe')
        self.assertEqual(assignments[0].c.text, 'is')
        self.assertEqual(assignments[0].sentence.text, 'Peter is a spider on my shoe')

        s = Sentence('currently, Robert is drafting its 1998 annual report')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0].p.text, 'Robert')
        self.assertEqual(assignments[0].n.text, 'drafting its 1998 annual___report')
        self.assertEqual(assignments[0].c.text, 'is')
        self.assertEqual(assignments[0].sentence.text, 'currently , Robert is drafting its 1998 annual report')

        s = Sentence('Robert is pretty tasty')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0].p.text, 'Robert')
        self.assertEqual(assignments[0].n.text, 'beautiful___tasty')
        self.assertEqual(assignments[0].c.text, 'is')
        self.assertEqual(assignments[0].sentence.text, 'Robert is beautiful tasty')

        s = Sentence('Robert is really sorry')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0].p.text, 'Robert')
        self.assertEqual(assignments[0].n.text, 'really sorry')
        self.assertEqual(assignments[0].c.text, 'is')
        self.assertEqual(assignments[0].sentence.text, 'Robert is really sorry')

        s = Sentence('I think Dr. jones is a tool')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0].p.text, 'Dr jones')
        self.assertEqual(assignments[0].n.text, 'a tool')
        self.assertEqual(assignments[0].c.text, 'is')
        self.assertEqual(assignments[0].sentence.text, 'I think Dr jones is a tool')

    def test_tricky_assignments(self):

        # Has good content but what to do with extra?
        s = Sentence('Robert is certain that the Secret Service agents will report the episode to the proper authorities')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0].p.text, 'Robert')
        self.assertEqual(assignments[0].n.text, 'definite that the_Secret_Service agents will report the episode to the true authorities')
        self.assertEqual(assignments[0].c.text, 'is')
        self.assertEqual(assignments[0].sentence.text, 'Robert is definite that the_Secret_Service agents will report the episode to the right authorities')

        s = Sentence('Not as far as Robert is concerned')  # robert is concerned... but I ain't
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0].p.text, 'Robert')
        self.assertEqual(assignments[0].n.text, 'concerned')
        self.assertEqual(assignments[0].c.text, 'is')
        self.assertEqual(assignments[0].sentence.text, 'Not as far as Robert is concerned')

        s = Sentence('Robert is in this holding pattern')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0].p.text, 'Robert')
        self.assertEqual(assignments[0].n.text, 'in this holding pattern')
        self.assertEqual(assignments[0].c.text, 'is')
        self.assertEqual(assignments[0].sentence.text, 'Robert is in this holding pattern')

        s = Sentence('What are you thinking?')
        deptree = s.deptree
        for d in deptree.nodes:
            print(d.serialize_line())
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0].p.text, 'What')
        self.assertEqual(assignments[0].n.text, 'you thinking ?')
        self.assertEqual(assignments[0].c.text, 'are')
        self.assertEqual(assignments[0].sentence.text, 'What are you thinking ?')

        raise Exception()

        #s = Sentence('Equally disturbing to Robert is the thought that it is difficult to explain Tippit’s death unless it was an attempt to escape arrest for the assassination of the president')
        #assignments = s.assignments
        #self.assertEqual(len(assignments), 3)
        #self.assertEqual(assignments[0].p.text, 'Robert')
        ##self.assertEqual(assignments[0].n.text, 'idea')
        #self.assertEqual(assignments[0].c.text, 'is')
        ##self.assertEqual(assignments[0].extra, 'that it is difficult to tell Tippit ’ s death unless it was attempt to escape arrest for assassination of president') 
        #self.assertEqual(assignments[0].sentence.text, 'Equally disturbing to Robert is the idea that it is difficult to tell Tippit ’ s death unless it was an attempt to escape arrest for the assassination of the president')

    def test_person_extract(self):
        s = Sentence('I want to talk to dr. jones')
        self.assertEqual(s.people, ['dr jones'])
        self.assertEqual(
            [o.text for o in s.segments],
            ['I', 'want', 'to', 'talk', 'to', 'dr jones']
        )
        s = Sentence('I want to talk to dr jones')
        self.assertEqual(
            [o.text for o in s.segments],
            ['I', 'want', 'to', 'talk', 'to', 'dr jones']
        )

        s = Sentence('I want to talk to mr jones')
        self.assertEqual(s.people, ['mr jones'])
        self.assertEqual(
            [o.text for o in s.segments],
            ['I', 'want', 'to', 'talk', 'to', 'mr jones']
        )
        s = Sentence('I want to talk to mr. jones')
        self.assertEqual(
            [o.text for o in s.segments],
            ['I', 'want', 'to', 'talk', 'to', 'mr jones']
        )

        s = Sentence('I want to talk to Tom Jones right now')
        self.assertEqual(s.people, ['Tom Jones'])
        self.assertEqual(
            [o.text for o in s.segments],
            ['I', 'want', 'to', 'talk', 'to', 'Tom Jones', 'right', 'now']
        )

    def test_minister_assign(self):
        s = Sentence('The minister for transport is a tit')
        self.assertEqual(s.people, ['minister for transport'])
        self.assertEqual(
            [o.text for o in s.segments],
            ['The', 'minister for transport', 'is', 'a', 'tit']
        )
        assignments = s.assignments

        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0].p.text, 'minister for transport')
        self.assertEqual(assignments[0].n.text, 'a tit')
        self.assertEqual(assignments[0].c.text, 'is')
        self.assertEqual(assignments[0].sentence.text, 'The minister_for_transport is a tit')

    def test_minister_person_parse(self):
        s = Sentence('The minister for transport something something')
        self.assertEqual(s.people, ['minister for transport'])

    def test_segments(self):
        s = Sentence('This is a sentence.')
        self.assertEqual(
            [o.text for o in s.segments],
            ['This', 'is', 'a', 'sentence', '.']
        )

        # since voluntary groups is a joining phrase
        s = Sentence('Can you please do something about voluntary groups?')
        self.assertEqual(
            [o.text for o in s.segments],
            ['Can', 'you', 'please', 'do', 'something', 'about', 'voluntary groups', '?']
        )

        s = Sentence('The first about dog food')
        self.assertEqual(
            [o.text for o in s.segments],
            ['The', 'first', 'about', 'dog food']
        )
        self.assertEqual(
            [o.tag for o in s.segments],
            ['DT', 'ORDINAL', 'IN', 'dunno']
        )


class TestSegment(TestCase):

    def test_tag(self):
        self.assertEqual(
            Segment('blah', tag='wooooo').tag,
            'wooooo'
        )
        self.assertEqual(
            Segment('I').tag,
            'PRP'
        )
        self.assertEqual(
            Segment('a phrase').tag,
            'dunno'
        )

    def test_is_entity(self):
        self.assertTrue(Segment('asd.', tag='DATE').is_entity)
        self.assertFalse(Segment('asd.', tag='NN').is_entity)

    def test_is_word(self):
        self.assertFalse(Segment('asd.').is_wordy)
        self.assertFalse(Segment('asd,').is_wordy)
        self.assertTrue(Segment('asd ').is_wordy)

    def test_lem_stem(self):
        self.assertEqual(Segment('bats').lem_stem, 'bat')


class TestSynonym(TestCase):

    def test_synonym(self):

        s = Synonym()
        self.assertEqual(s.get_word('large'), 'big')
        self.assertEqual(s.get_word('asdasdasd'), 'asdasdasd')

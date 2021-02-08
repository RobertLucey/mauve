
from unittest import TestCase
import mock

import glob
import os

from mauve.models.segment import Segment
from mauve.models.sentence import Sentence
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
        self.assertEqual(assignments[0][0].text, 'Robert')
        self.assertEqual(assignments[0][2].text, 'the first person to shove a golf___ball up their nose')
        self.assertEqual(assignments[0][1].text, 'is')

    def test_get_assignments(self):

        s = Sentence('Tom Jones is happy')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0][0].text, 'Tom___Jones') # FIXME This should be a person in a while
        self.assertEqual(assignments[0][2].text, 'happy')
        self.assertEqual(assignments[0][1].text, 'is')

        s = Sentence('Tom Jones is happy about it')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0][0].text, 'Tom___Jones')
        self.assertEqual(assignments[0][2].text, 'happy about it')
        self.assertEqual(assignments[0][1].text, 'is')

        s = Sentence('Robert are fun')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0][0].text, 'Robert')
        self.assertEqual(assignments[0][2].text, 'fun')
        self.assertEqual(assignments[0][1].text, 'are')

        s = Sentence('Robert are not fun')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0][0].text, 'Robert')
        self.assertEqual(assignments[0][2].text, 'not fun')
        self.assertEqual(assignments[0][1].text, 'are')

        s = Sentence('Peter is a spider on my shoe')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0][0].text, 'Peter')
        self.assertEqual(assignments[0][2].text, 'a spider on my shoe')
        self.assertEqual(assignments[0][1].text, 'is')

        s = Sentence('currently, Robert is drafting its 1998 annual report')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0][0].text, 'Robert')
        self.assertEqual(assignments[0][2].text, 'drafting its 1998 annual___report')
        self.assertEqual(assignments[0][1].text, 'is')

        s = Sentence('Robert is pretty tasty')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0][0].text, 'Robert')
        self.assertEqual(assignments[0][2].text, 'beautiful___tasty')
        self.assertEqual(assignments[0][1].text, 'is')

        s = Sentence('Robert is really sorry')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0][0].text, 'Robert')
        self.assertEqual(assignments[0][2].text, 'really sorry')
        self.assertEqual(assignments[0][1].text, 'is')

        s = Sentence('I think Dr. Jones is a tool')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0][0].text, 'Dr___Jones')
        self.assertEqual(assignments[0][2].text, 'a tool')
        self.assertEqual(assignments[0][1].text, 'is')

    def test_tricky_assignments(self):

        # Has good content but what to do with extra?
        s = Sentence('Robert is certain that the Secret Service agents will report the episode to the proper authorities')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0][0].text, 'Robert')
        self.assertEqual(assignments[0][2].text, 'definite that the___Secret___Service___agents will report the episode to the true authorities')
        self.assertEqual(assignments[0][1].text, 'is')

        s = Sentence('Not as far as Robert is concerned')  # robert is concerned... but I ain't
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0][0].text, 'Robert')
        self.assertEqual(assignments[0][2].text, 'concerned')
        self.assertEqual(assignments[0][1].text, 'is')

        s = Sentence('Robert is in this holding pattern')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0][0].text, 'Robert')
        self.assertEqual(assignments[0][2].text, 'in this holding pattern')
        self.assertEqual(assignments[0][1].text, 'is')

        s = Sentence('What are you thinking?')
        assignments = s.assignments
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0][0].text, 'What')
        self.assertEqual(assignments[0][2].text, 'you thinking')
        self.assertEqual(assignments[0][1].text, 'are')

        s = Sentence('Equally disturbing to Robert is the thought that it is difficult to explain Tippit’s death unless it was an attempt to escape arrest for the assassination of the president')
        assignments = s.assignments
        self.assertEqual(len(assignments), 3)
        self.assertEqual(assignments[0][0].text, 'Robert')
        self.assertEqual(assignments[0][1].text, 'is')
        self.assertEqual(assignments[1][0].text, 'it')
        self.assertEqual(assignments[1][1].text, 'is')
        self.assertEqual(assignments[2][0].text, 'it')
        self.assertEqual(assignments[2][1].text, 'was')

    def test_person_extract(self):

        s = Sentence('I want to talk to dr. Jones')
        self.assertEqual([p.name for p in s.people], ['dr Jones'])
        self.assertEqual(
            [o.text for o in s.segments],
            ['I', 'want', 'to', 'talk', 'to', 'dr Jones']
        )
        s = Sentence('I want to talk to dr Jones')
        self.assertEqual(
            [o.text for o in s.segments],
            ['I', 'want', 'to', 'talk', 'to', 'dr Jones']
        )

        s = Sentence('I want to talk to mr Jones')
        self.assertEqual([p.name for p in s.people], ['mr Jones'])
        self.assertEqual(
            [o.text for o in s.segments],
            ['I', 'want', 'to', 'talk', 'to', 'mr Jones']
        )
        s = Sentence('I want to talk to mr. Jones')
        self.assertEqual(
            [o.text for o in s.segments],
            ['I', 'want', 'to', 'talk', 'to', 'mr Jones']
        )

        s = Sentence('I want to talk to Tom Jones right now')
        self.assertEqual([p.name for p in s.people], ['Tom Jones'])
        self.assertEqual(
            [o.text for o in s.segments],
            ['I', 'want', 'to', 'talk', 'to', 'Tom Jones', 'right', 'now']
        )

    def test_minister_assign(self):
        s = Sentence('The minister for transport is a tit')
        self.assertEqual([p.name for p in s.people], ['minister for transport'])
        self.assertEqual(
            [o.text for o in s.segments],
            ['The', 'minister for transport', 'is', 'a', 'tit']
        )
        assignments = s.assignments

        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0][0].text, 'minister_for_transport')  # FIXME This should be a person in a while
        self.assertEqual(assignments[0][2].text, 'a tit')
        self.assertEqual(assignments[0][1].text, 'is')

    def test_minister_person_parse(self):
        s = Sentence('The minister for transport something something')
        self.assertEqual([p.name for p in s.people], ['minister for transport'])

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

    def test_lvr_boring(self):
        lvr = Sentence('la la la').lvr
        self.assertEqual(lvr, [])

    def test_lvr_assignment(self):
        lvr = Sentence('This is strange').lvr
        self.assertEqual(len(lvr), 1)
        self.assertEqual(lvr[0][0].text, 'This')
        self.assertEqual(lvr[0][1].text, 'is')
        self.assertEqual(lvr[0][2].text, 'strange')

    def test_lvr_conditional(self):
        lvr = Sentence('You can have some chocolate if you want').lvr
        self.assertEqual(lvr[0][0].text, 'you want')
        self.assertEqual(lvr[0][1].text, 'if')
        self.assertEqual(lvr[0][2].text, 'You can have some chocolate')

    def test_lvr_assignment_and_conditional(self):
        lvr = Sentence('This is a weird test if it was failing').lvr
        self.assertEquals(lvr[0][0].text, 'This')
        self.assertEquals(lvr[0][1].text, 'is')
        self.assertEquals(lvr[0][2].text, 'a strange___test if it was failing')
        self.assertEquals(lvr[0][2].lvr[0][0].text, 'it')
        self.assertEquals(lvr[0][2].lvr[0][1].text, 'was')
        self.assertEquals(lvr[0][2].lvr[0][2].text, 'failing')

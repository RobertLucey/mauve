# Mauve

[![Build Status](https://travis-ci.com/RobertLucey/mauve.svg?branch=master)](https://travis-ci.com/RobertLucey/mauve)

ORM-ing a book and using it for finding interesting stats.

Inspiration from the book "Nabokov's Favorite Word Is Mauve".

## Given Data

There is data [here](data/) of some details of 10k books to play with.

## Features

* Tools
  * Scraping
    * Books from:
      * Calibre websites
      * The Eye
    * Metadata from:
      * Goodreads including
        * Genre
        * Reviews
      * Wikipedia for:
        * Author birth year
        * Author nationality
    * Political debates from:
      * From api.oireachtas.ie
  * Mobi to Epub conversion
  * Epub conversion to text
  * Removal of images / fonts from epubs to keep required storage to a minimum
  * Compression of preprocessed content to keep required storage to a minimum
* Classification
  * Guess the following of a book from training over a load of scraped data:
    * Author gender (>80% accuracy)
    * Which author (requires >= 2 books per author being used) (Accuracy good but depends highly on how many authors and how many minimum required books per author)
    * Author nationality (>80% accuracy in a sample of 50 of each British, Australia, United States, Canada, India, Ireland, France)
    * Author age
    * book published year
    * TODO: lots more
* (Interesting) properties of a book:
  * Time it should take to read the text
  * How difficult the language in the book is
  * Author gender
  * Author nationality
  * Author birth year
    * Fun to use with the published date to compare how people write based on their age
  * Average rating out of 5 (from goodreads)
  * Genres (from goodreads)
  * Lexical diversity
  * Profanity score (how profane the content is)
  * Positive / negative sentiment
  * People within the text
    * Extracts the names of people in the text. Gets the gender of these people too
  * Assignments
  * Things by people
    * From speech items:
      * Sentiment of speech by person
      * Assignments they use (if Bob says "Alice is a fool" you can extract to see what Bob says about Alice)
      * Profanity
      * Sentiment
* Comparisons between books
  * Word usage by group
    * Get the usage (by %) difference between groups like author gender / nationality / genre / publication date / whatever. Tries to ignore boring words which is essentially an extended stopwords set


## Usage

Load of things you can do, I'll just include some interesting ones here.

```python
>>> from mauve.models.text import TextBody
>>> text = TextBody(content='“You are not attending!” said the Mouse to Alice severely. “What are you thinking of?”')
>>> text.people.serialize()
[{'name': 'Mouse', 'gender': None}, {'name': 'Alice', 'gender': 'female'}]

>>> text.get_speech_by_people()['Mouse'][0].serialize()
{'text': 'You are not attending !', 'speaker': {'name': 'Mouse', 'gender': None}, 'inflection': 'said'}

>>> assignment = text.assignments[0]
>>> 'The assignment is that "{variable}" "{assigning_word}" "{value}"'.format(variable=assignment[0].text, assigning_word=assignment[1].text, value=assignment[2].text)
The assignment is that "You" "are" "not attending"

>>> TextBody(content='London is the capital of Paris, and Paris is the capital of Rome').get_assignments_by('Paris')
['the capital of Rome']

>>> text = TextBody(content='“Bad no this sucks” said the Mouse to Alice. Alice replied, “Happy Love”')
>>> text.get_sentiment_by_people()
{'Mouse': {'neg': 0.647, 'neu': 0.114, 'pos': 0.24, 'compound': -0.5559}, 'Alice': {'neg': 0.0, 'neu': 0.0, 'pos': 1.0, 'compound': 0.836}}

>>> TextBody(content='“This is a load of ass!” said the Mouse').get_profanity_score()
1111.111111111111
>>> TextBody(content='“This is a load of ass!” said the Mouse to Alice severely. “That\'s rude my dude” whispered Alice').get_profanity_by_people()
{'Mouse': 1666.6666666666667, 'Alice': 0}
```

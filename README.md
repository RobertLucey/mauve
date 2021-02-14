# Mauve

[![Build Status](https://travis-ci.com/RobertLucey/mauve.svg?branch=master)](https://travis-ci.com/RobertLucey/mauve)

Inspiration from the book "Nabokov's Favorite Word Is Mauve".
Essentially an ebook scraper for the moment but intending on doing local analysis soon. Doing analysis in splunk at the moment.

## Usage

Load of things you can do, I'll just include some interesting ones here.

```python
>> from mauve.models.text import TextBody
>> text = TextBody(content='“You are not attending!” said the Mouse to Alice severely. “What are you thinking of?”')
>> text.people.serialize()
[{'name': 'Mouse', 'gender': None}, {'name': 'Alice', 'gender': 'female'}]
>> text.get_speech_by_people()['Mouse'][0].serialize()
{'text': 'You are not attending !', 'speaker': {'name': 'Mouse', 'gender': None}, 'inflection': 'said'}
>> assignment = text.assignments[0]
>> 'The assignment is that "{variable}" "{assigning_word}" "{value}"'.format(variable=assignment[0].text, assigning_word=assignment[1].text, value=assignment[2].text)
The assignment is that "You" "are" "not attending"

>> text = TextBody(content='“Bad no this sucks” said the Mouse to Alice. Alice replied, “Happy Love”')
>> text.get_sentiment_by_people()
{'Mouse': {'neg': 0.647, 'neu': 0.114, 'pos': 0.24, 'compound': -0.5559}, 'Alice': {'neg': 0.0, 'neu': 0.0, 'pos': 1.0, 'compound': 0.836}}

>> TextBody(content='“This is a load of ass!” said the Mouse').get_profanity_score()
833.3333333333334
>> TextBody(content='“This is a load of ass!” said the Mouse to Alice severely. “That\'s rude my dude” whispered Alice').get_profanity_by_people()
{'Mouse': 1428.5714285714287, 'Alice': 0}
```

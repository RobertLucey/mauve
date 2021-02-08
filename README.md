# Mauve

Inspiration from the book "Nabokov's Favorite Word Is Mauve".
Essentially an ebook scraper for the moment but intending on doing local analysis soon. Doing analysis in splunk at the moment.

## Usage

Load of things you can do, I'll just include some interesting ones here.

```python
>> from mauve.models.text import TextBody
>> text = TextBody(content='“You are not attending!” said the Mouse to Alice severely. “What are you thinking of?”')
>> text.people.serialize()
[{'name': 'Mouse', 'gender': None}, {'name': 'Alice', 'gender': 'female'}]
>> text.get_speech_by_person()
defaultdict(<class 'list'>, {'Mouse': ['You are not attending !'], '': ['What are you thinking of ?']})
>> assignment = text.assignments[0][0]
>> print('The assignment is that "{variable}" "{assigning_word}" "{value}"'.format(variable=assignment[0].text, assigning_word=assignment[1].text, value=assignment[2].text))
The assignment is that "You" "are" "not attending"

>> text = TextBody(content='“Bad no this sucks” said the Mouse to Alice. Alice replied, “Happy Love”')
>> print(text.get_sentiment_by_person())
[{'name': 'Mouse', 'sentiment': {'neg': 0.647, 'neu': 0.114, 'pos': 0.24, 'compound': -0.5559}}, {'name': 'Alice', 'sentiment': {'neg': 0.0, 'neu': 0.0, 'pos': 1.0, 'compound': 0.836}}]
```

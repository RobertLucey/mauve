# Data

Here's some data I've processed so you don't have to

Caveats:
* Generally it's of books where there are more than 10 reviews
* Sentiment only takes 5% of the text cause it takes ages to process. Generally fairly accurate but will work on not having to do this

I'll update whenever an attribute is added or improved

[Here's a set of fiction books you can use as a plaything](fiction.csv) containing 10k fiction books

As more things are made I'll add them into the given data. There are some things that would add too much data so they won't be included

The interesting fields given are:

- isbn (There is an isbn13 stored but I don't want to make the data file too big)
- title
- author (name)
- author_gender
- author_nationality
- author_birth_year
- year_published
- avg_rating (goodreads)
- num_ratings (goodreads)
- adjective_score (number of adjectives per 10k words)
- adverb_score (number of adverbs per 10k words)
- flesch_reading_ease_score (textstats version, probably going to remove at some point)
- lexical_diversity (len(set(self.words)) / len(self.words))
- word_count
- count_exclamation_marks (number of exclamation marks per 10k words)
- count_question_marks (number of question marks per 10k words)
- profanity_score (number of profane words / phrases per 10k words)
- sentiment_neg_score (vader negative score)
- sentiment_pos_score (vader positive score)
- sentiment_compound_score (vader compound score)
- reading_difficulty (custom metric for how difficult the book is to read)
- reading_time (how long the book should take to read)



For more complete data:

[TODO Here's all the books](books.csv)

[TODO Here's all the genres associated with the book](genres.csv)

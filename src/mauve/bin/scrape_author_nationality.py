import json
import re
from multiprocessing.pool import ThreadPool
import dateutil.parser as dparser
from urllib.parse import quote
from urllib.request import urlopen

import bs4

from mauve.utils import iter_books
from mauve.constants import AUTHOR_METADATA_PATH


BASE_COUNTRIES = ['United States', 'Afghanistan', 'Albania', 'Algeria', 'American Samoa', 'Andorra', 'Angola', 'Anguilla', 'Antarctica', 'Antigua And Barbuda', 'Argentina', 'Armenia', 'Aruba', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bermuda', 'Bhutan', 'Bolivia', 'Bosnia And Herzegowina', 'Botswana', 'Bouvet Island', 'Brazil', 'Brunei Darussalam', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cambodia', 'Cameroon', 'Canada', 'Cape Verde', 'Cayman Islands', 'Central African Rep', 'Chad', 'Chile', 'China', 'Christmas Island', 'Cocos Islands', 'Colombia', 'Comoros', 'Congo', 'Cook Islands', 'Costa Rica', 'Cote D`ivoire', 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'East Timor', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Ethiopia', 'Falkland Islands', 'Faroe Islands', 'Fiji', 'Finland', 'France', 'French Guiana', 'French Polynesia', 'French S. Territories', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Gibraltar', 'Greece', 'Greenland', 'Grenada', 'Guadeloupe', 'Guam', 'Guatemala', 'Guinea', 'Guinea-bissau', 'Guyana', 'Haiti', 'Honduras', 'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'North Korea', 'South Korea', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macau', 'Macedonia', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Martinique', 'Mauritania', 'Mauritius', 'Mayotte', 'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montserrat', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'Netherlands Antilles', 'New Caledonia', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Niue', 'Norfolk Island', 'Northern Mariana Islands', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Pitcairn', 'Poland', 'Portugal', 'Puerto Rico', 'Qatar', 'Reunion', 'Romania', 'Russian Federation', 'Rwanda', 'Saint Kitts And Nevis', 'Saint Lucia', 'St Vincent/Grenadines', 'Samoa', 'San Marino', 'Sao Tome', 'Saudi Arabia', 'Senegal', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'Spain', 'Sri Lanka', 'St. Helena', 'St.Pierre', 'Sudan', 'Suriname', 'Swaziland', 'Sweden', 'Switzerland', 'Syrian Arab Republic', 'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Togo', 'Tokelau', 'Tonga', 'Trinidad And Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City State', 'Venezuela', 'Viet Nam', 'Virgin Islands (British)', 'Virgin Islands (U.S.)', 'Western Sahara', 'Yemen', 'Yugoslavia', 'Zaire', 'Zambia', 'Zimbabwe']

# For ambiguous names or nationalities rather than country names
EXTRA_COUNTRIES_MAP = {'Czech': 'Czech Republic', 'Canadian': 'Canada', 'U.S.': 'United States', 'New York': 'United States', 'Ohio': 'United States', 'American': 'United States', 'America': 'United States', 'Georgia': 'United States', 'US': 'United States', 'USA': 'United States', 'United States of America': 'United States', 'US citizen': 'United States', 'England': 'England', 'English': 'England', 'Hungarian': 'Hungary', 'Peruvian': 'Peru', 'French': 'France', 'Colombian': 'Colombia', 'Danish': 'Denmark', 'Scotland': 'Scotland', 'Egyptian': 'Egypt', 'Lebanese': 'Lebanon', 'Chinese': 'China', 'Swedish': 'Sweden', 'Yugoslav': 'Yugoslavia', 'Welsh': 'Wales', 'Wales': 'Wales', 'Northern Ireland': 'Northern Ireland', 'Holy Roman Empire': 'Holy Roman Empire', 'South African': 'South Africa', 'Nigerian': 'Nigeria', 'Chilean': 'Chile', 'Australian': 'Australia', 'Austrian': 'Austria', 'New Zealander': 'New Zealand', 'Norwegian': 'Norway', 'Scottish': 'Scotland', 'Polish': 'Poland', 'Spanish': 'Spain', 'Israeli': 'Israel', 'Irish': 'Ireland', 'Japanese': 'Japan', 'Italian': 'Italy', 'Jamaican': 'Jamaica', 'Indian': 'India', 'German': 'Germany', 'Mexican': 'Mexico'}

COUNTRIES = BASE_COUNTRIES + list(EXTRA_COUNTRIES_MAP.keys())

SEARCH = 'https://en.wikipedia.org/w/index.php?search={name}&title=Special%3ASearch&fulltext=1&ns0=1'


def clean_person(person):

    def parse_birth_year(birth_year):
        if birth_year is None:
            return None
        return birth_year if birth_year < 2020 and birth_year > 1000 else None

    def parse_nationality(nationality):
        # TODO: clean dual citizen
        return EXTRA_COUNTRIES_MAP.get(nationality, nationality)

    return {
        'born': parse_birth_year(person['born']),
        'nationality': parse_nationality(person['nationality'])
    }


def get_wikipedia_person_by_href(href):
    """
        Problematic /wiki/Glen_Cook
    """
    soup = bs4.BeautifulSoup(
        urlopen(
            'https://wikipedia.org' + href
        ),
        'html.parser'
    )

    if 'author' in soup.text:  # FIXME this might be disambig

        birth_year = None
        nationality = None

        info = soup.find('table', class_='infobox')
        if info is None:
            return {
                'born': birth_year,
                'nationality': nationality
            }

        for row in info.find_all('tr'):
            if row.text.lower().startswith('born'):
                for country in COUNTRIES:
                    if country in row.text:
                        nationality = country

                try:
                    birth_year = dparser.parse(
                        row.find('span', {'class', 'dtstart bday'}).text,
                        fuzzy=True
                    ).year
                except:
                    pass

                try:
                    birth_year = dparser.parse(
                        row.find('span', {'class', 'bday'}).text,
                        fuzzy=True
                    ).year
                except:
                    pass

                try:
                    birth_year = int(
                        row.find(
                            'td',
                            {'style': 'line-height:1.4em;'}
                        ).text.split(' ')[0]
                    )
                except:
                    pass

                try:
                    birth_year = int(
                        row.find(
                            'td',
                            {'style': 'line-height:1.4em;'}
                        ).contents[0]
                    )
                except:
                    pass

                numbers = [int(s) for s in row.text.split() if s.isdigit()]
                likely_years = [i for i in numbers if i > 1600 and i < 2100]
                if len(likely_years) == 1:
                    birth_year = likely_years[0]

            elif 'Nationality' in row.text:
                nationality = row.text.replace('Nationality', '')

        if nationality is not None:
            nationality = re.sub(r'\[.*\]', '', nationality).strip()
            nationality = re.sub(r'\(.*\)', '', nationality).strip()

        if birth_year is None or nationality is None:
            pass  # TODO: debug here for getting more

        return {
            'born': birth_year,
            'nationality': nationality
        }

    return {
        'born': None,
        'nationality': None
    }


def get_wikipedia_person_by_book(book):
    source = urlopen(
        SEARCH.format(
            name=quote(book.author.name)
        )
    )
    soup = bs4.BeautifulSoup(source, 'html.parser')
    results = soup.find_all('div', {'class': 'mw-search-result-heading'})

    authors = [
        i for i in results if all([
            '(author)' in i.a.get('href').lower(),
            book.author.name.replace(' ', '_') in i.a.get('href')
        ])
    ]

    person = None
    if authors:
        person = get_wikipedia_person_by_href(authors[0].a.get('href'))
    else:
        for result in results:
            if result.text.strip() == book.author.name.strip():
                person = get_wikipedia_person_by_href(result.a.get('href'))

    if isinstance(person, dict):
        return (
            book.author.name,
            clean_person({
                'born': person.get('born', None),
                'nationality': person.get('nationality', None)
            })
        )
    else:
        return (
            book.author.name,
            clean_person({
                'born': None,
                'nationality': None
            })
        )


def get_wikisearch_people(stop_after=1000):
    people = {}
    with open(AUTHOR_METADATA_PATH, 'r') as f:
        for k, v in json.loads(f.read()).items():
            people[k] = clean_person(v)

    books = []
    for idx, book in enumerate(iter_books()):
        if idx == stop_after:
            break
        if book.author.name in people.keys():
            if people[book.author.name]['born'] is not None and people[book.author.name]['nationality'] is not None:
                continue
            books.append(book)

    people_responses = []
    with ThreadPool(processes=20) as pool:
        people_responses.extend(
            pool.map(
                get_wikipedia_person_by_book,
                books
            )
        )

    people.update({p[0]: p[1] for p in people_responses})

    return people


def main():
    people = get_wikisearch_people(stop_after=100000)
    with open(AUTHOR_METADATA_PATH, 'w') as f:
        f.write(json.dumps(people))


if __name__ == '__main__':
    main()

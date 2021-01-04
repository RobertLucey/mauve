from setuptools import (
    find_packages,
    setup
)

INSTALL_REQUIRES = [
    'scapy',
    'textacy',
    'nltk',
    'cached_property',
    'fast_json',
    'bs4',
    'profanity',
    'boto3',
    'gender-guesser',
    'langdetect'
]

setup(
    name='mauve',
    description='Unit test your writing',
    version='0.0.1',
    python_requires='>3.5',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=INSTALL_REQUIRES,
    entry_points={
        'console_scripts': [
        ]
    }
)

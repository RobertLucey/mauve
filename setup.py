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
    'langdetect',
    'tqdm',
    'textstat',
    'vaderSentiment'
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
            'mauve_convert_filenames = mauve.bin.convert_filenames:main',
            'mauve_load_tokens = mauve.bin.load_tokens:main',
            'mauve_epub_slimmer = mauve.bin.rm_images:main',
            'mauve_scrape_calibre = mauve.bin.scrape_calibre:main',
            'mauve_scrape_eye = mauve.bin.scrape_eye:main',
            'mauve_scrape_goodreads = mauve.bin.scrape_goodreads:main',
            'mauve_epub_to_text = mauve.bin.to_text:main',
        ]
    }
)

from setuptools import (
    find_packages,
    setup
)

INSTALL_REQUIRES = [
    'transformers',
    'torch==1.8.0',
    'datasets==1.5.0',
    'faiss-cpu',
    'compress-pickle<2.0.0',
    'pandas',
    'scapy',
    'textacy==0.10.1',
    'nltk',
    'cached_property',
    'fast_json',
    'bs4',
    'boto3',
    'gender-guesser',
    'langdetect',
    'tqdm',
    'textstat',
    'vaderSentiment',
    'EbookLib',
    'tika',
    'spacy_wordnet',
    'gensim',
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
            'mauve_scrape_oireachtas = mauve.bin.scrape_oireachtas:main',
            'mauve_scrape_calibre = mauve.bin.scrape_calibre:main',
            'mauve_scrape_eye = mauve.bin.scrape_eye:main',
            'mauve_scrape_goodreads = mauve.bin.scrape_goodreads:main',
            'mauve_scrape_author_nationality = mauve.bin.scrape_author_nationality:main',
            'mauve_convert_filenames = mauve.bin.convert_filenames:main',
            'mauve_load_tokens = mauve.bin.load_tokens:main',
            'mauve_epub_slimmer = mauve.bin.epub_slimmer:main',
            'mauve_mobi_to_epub = mauve.bin.mobi_to_epub:main',
            'mauve_epub_to_text = mauve.bin.to_text:main',
            'mauve_compress_files = mauve.bin.compress_files:main',
            'mauve_generate_rag = mauve.bin.generate_rag:main',
        ]
    }
)

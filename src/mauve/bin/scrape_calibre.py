from urllib.request import (
    urlopen,
    urlretrieve
)
import cgi

from mauve.utils import clean_filename


base_url = ''


def download(book_id):
    try:
        dl_url = base_url + '/get/EPUB/{}/Calibre_Library'.format(book_id)

        remotefile = urlopen(dl_url)
        blah = remotefile.info()['Content-Disposition']
        value, params = cgi.parse_header(blah)

        try:
            title, author = params['filename'].split('_')[0].split(' - ')  # NOTE: may need to modify this
            filename = 'NOPE___%s___%s.epub' % (author, title)
            filename = '/opt/mauve/epub/' + clean_filename(filename)
            urlretrieve(dl_url, filename)
        except:
            raise Exception
    except Exception as ex:
        print('%s %s' % (book_id, ex))
        return None

book_ids = range(0, 100)  # TODO: config yourself

# TODO: pool it if using again
for book_id in book_ids:
    download(book_id)

import requests
import sqlite3
import zlib
import census.utils

"""An extremely basic (and possibly unreliable) 'caching proxy server'.

To clear the cache, delete cache/cache.db.
"""

def _get_page_from_cache(con, url):
    try:
        cur = con.cursor()
        cur.execute('SELECT page FROM cache WHERE url=?', (url,))
        result = zlib.decompress(cur.fetchone()[0]).decode("utf-8")
        return result
    except:
        return None

def get_page(url):
    """Return the body of the page at `url`.

    If the request page isn't already in the SQLite database cache/cache.db,
    it is added there.  If it is already in the database, the stored copy is
    returned in order to avoid an HTTP GET request.
    """
    census.utils.mkdir_p('cache')
    con = sqlite3.connect('cache/cache.db')
    page = _get_page_from_cache(con, url)
    if page is None:
        response = requests.get(url)
        if response.status_code != requests.codes.ok:
            raise ValueError('Unexpected status code from Nomis API: {} for URL {}'.format(
            response.status_code,
            url
        ))
        page = response.text
        con.execute('''CREATE TABLE IF NOT EXISTS cache
                   (url text, page blob)''')
        # Store URL and compressed page in database
        con.execute('INSERT INTO cache values (?,?)',
                (url, zlib.compress(page.encode("utf-8"))))
        con.commit()
        con.close()
    return page

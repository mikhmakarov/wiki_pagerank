import requests
import logging
import threading

from time import sleep
from urllib.parse import urljoin, unquote
from collections import deque, namedtuple
from bs4 import BeautifulSoup, SoupStrainer

f = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(format=f, datefmt='%Y-%m-%d %H:%M:%S', level='INFO')

logger = logging.getLogger('logger')


SEED_PAGE = 'https://ru.wikipedia.org/wiki/%D0%92%D1%8B%D1%81%D1%88%D0%B0%D1%8F_%D1%88%D0%BA%D0%BE%D0%BB%' \
            'D0%B0_%D1%8D%D0%BA%D0%BE%D0%BD%D0%BE%D0%BC%D0%B8%D0%BA%D0%B8'
DOMAIN = 'https://ru.wikipedia.org'
TMP_RESULTS_FILENAME = 'tmp_results'
DUMP_NMBR = 100


Result = namedtuple('Result', ['url', 'links'])


class WikiCrawler(object):
    def __init__(self):
        self._reset()

    def _reset(self):
        self.domain = DOMAIN
        self.pages = deque([SEED_PAGE])
        self.dangling_pages = {}
        self.visited = {}
        self.results = []
        self.tmp_filename = TMP_RESULTS_FILENAME
        self.results_cnt = 0

        with open(self.tmp_filename, 'w') as out:
            out.write('')

    def dump_results(self):
        self.results_cnt += DUMP_NMBR

        with open(self.tmp_filename, 'a') as out:
            for res in self.results:
                out.write(','.join([unquote(res.url)] + [unquote(link) for link in res.links]) + '\n')

        logger.info('DUMPED %s results', self.results_cnt)
        self.results = []

    def dump_result(self, res, index):
        with open(self.tmp_filename + index + '.txt', 'a') as out:
            out.write(','.join([unquote(res.url)] + [unquote(link) for link in res.links]) + '\n')

    def get_links(self, s, page):
        try:
            response = s.get(page)
            only_a_tags = SoupStrainer("a")
            soup = BeautifulSoup(response.content, 'lxml', parse_only=only_a_tags)
            links = [obj.attrs['href'].split('#', 1)[0] for obj in soup.select('a') if 'href' in obj.attrs]
            links = [urljoin(self.domain, link) for link in links if link.startswith('/wiki') and ':' not in link]
            links = [link for link in links if link not in self.dangling_pages]

            return set(links)
        except:
            return []

    def crawl(self, index='1'):
        session = requests.Session()
        print('started')

        while True:
            if len(self.pages) > 0:

                page = self.pages.popleft()

                if page not in self.visited:
                    self.visited[page] = True
                    links = self.get_links(session, page)

                    if len(links) != 0:
                        self.pages.extend(links)
                        r = Result(url=page, links=links)
                        self.results.append(r)
                        self.dump_result(r, index)
                    else:
                        self.dangling_pages[page] = True

    def run(self):
        pool = []
        for i in range(4):
            t = threading.Thread(target=self.crawl, args=(str(i)))
            t.start()
            pool.append(t)
            sleep(10)

        for t in pool:
            t.join()


if __name__ == '__main__':
    wiki = WikiCrawler()
    wiki.run()
#    wiki.crawl()





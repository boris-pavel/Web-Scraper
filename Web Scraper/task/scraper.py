import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

URL = 'https://www.nature.com/nature/articles?sort=PubDate&year=2020'
PATH = r'C:\Users\boris\PycharmProjects\Web Scraper\Web Scraper\task'


class Scraper:
    def __init__(self, input_url):
        self.base_url = input_url
        self.response = requests.get(self.base_url, headers={'Accept-Language': 'en-US,en;q=0.5'})
        self.content = self.response.content
        self.soup = BeautifulSoup(self.content, 'html.parser')
        self.domain = urlparse(self.base_url).netloc
        self.url = self.base_url

    def change_page(self, page):
        self.response = requests.get(self.base_url, params={'page': page})
        self.url = self.response.url
        self.content = self.response.content
        self.soup = BeautifulSoup(self.content, 'html.parser')
        self.domain = urlparse(self.url).netloc


class NaturePage:
    def __init__(self, soup, domain, typ):
        self.article_type = typ
        self.soup = soup
        self.domain = domain

    def find_articles(self):
        articles = self.soup.find_all('article')
        for article in articles:
            span = article.find('span', attrs={'data-test': 'article.type'})
            article_type = span.text
            if article_type != self.article_type:
                continue

            a = article.find('a', attrs={'data-track-action': "view article"})
            title = re.sub(' ', '_', a.text.strip())
            title = re.sub('[^a-zA-Z_]', '', title)
            title += '.txt'

            article_link = 'https://' + self.domain + a.get('href')
            article_soup = BeautifulSoup(requests.get(article_link).content, 'html.parser')
            paragraph = article_soup.find('p', attrs={"class": "article__teaser"})

            self.save_articles(title, paragraph.text)

    @staticmethod
    def save_articles(t, p):
        file = open(t, 'wb')
        file.write(p.encode())
        file.close()


if __name__ == '__main__':
    pages_num = int(input())
    article_type = input()

    scraper = Scraper(URL)
    for i in range(1, pages_num + 1):
        scraper.change_page(i)
        page = NaturePage(scraper.soup, scraper.domain, article_type)

        os.mkdir(f'Page_{i}')
        os.chdir(f'Page_{i}')

        page.find_articles()

        os.chdir(PATH)

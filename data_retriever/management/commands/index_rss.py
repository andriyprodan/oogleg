import feedparser
import pandas as pd
from bs4 import BeautifulSoup
from django.core.management import BaseCommand

from articles.es_documents import ArticleDocument
from search.embeddings_storage import write_embeddings


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("url", type=str)

    def handle(self, *args, **options):
        feed = feedparser.parse(options['url'])
        # add data into elasticsearch
        pd_data = pd.DataFrame(columns=['url', 'title', 'abstract'])
        for entry in feed.entries:
            # remove html tags using regex

            abstract = ' '.join(abstract.split(' ')[:128])
            ad = ArticleDocument(_id=entry['id'], title=entry['title'], content=entry['fulltext'],
                                 abstract=abstract)
            ad.save()

            # machine learning part
            new_row = pd.DataFrame({'url': entry['id'], 'title': entry['title'], 'abstract': abstract}, index=[0])
            pd_data = pd.concat([pd_data, new_row], ignore_index=True)
        # write dense vectors to file
        write_embeddings(pd_data)

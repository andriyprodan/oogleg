import feedparser
import pandas as pd
from bs4 import BeautifulSoup
from django.core.management import BaseCommand

from articles.es_documents import ArticleDocument
from articles.models import WebResource
from search.embeddings_storage import write_embeddings


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("url", type=str)

    def handle(self, *args, **options):
        feed = feedparser.parse(options['url'])
        resources = []
        for entry in feed.entries:
            # remove html tags using regex

            wr = WebResource.objects.update_or_create(url=entry['id'],
                                                      defaults={'title': entry['title'], 'content': entry['fulltext']})
            resources.append(wr)

        # machine learning part
        # write dense vectors to file
        write_embeddings(resources)

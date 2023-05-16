import re
from html import unescape

import unicodedata
from bs4 import BeautifulSoup
from django.db import models

from neo4j_admin.driver import driver


class WebResource(models.Model):
    url = models.URLField(max_length=2000, unique=True, verbose_name='URL')
    title = models.CharField(max_length=2000, verbose_name='Заголовок')
    abstract = models.TextField(verbose_name='Анотація')
    content = models.TextField(verbose_name='Вміст')

    class Meta:
        verbose_name = 'Веб-ресурс'
        verbose_name_plural = 'Веб-ресурси'

    def __str__(self):
        return self.title

    @staticmethod
    def process_abstract(text: str):
        s = unicodedata.normalize('NFKC', unescape(text))
        return re.sub(r'\s+', ' ', s)

    def save(self, *args, **kwargs):
        soup = BeautifulSoup(self.content, 'html.parser')
        text_string = soup.get_text(separator=' ')
        self.abstract = self.process_abstract(self.title + ' ' + text_string)
        super().save(*args, **kwargs)

        #         save web resource as node in neo4j
        with driver.session() as session:
            session.run(
                f"MERGE (n:WebResource {{url: '{self.url}'}}) SET n.title = '{self.title}', n.abstract = '{self.abstract}', n.content = '{self.content}';")

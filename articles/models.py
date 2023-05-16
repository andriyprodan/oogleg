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
        self.abstract = " ".join(self.abstract.split(' ')[:128])
        super().save(*args, **kwargs)

        #         save web resource as node in neo4j
        with driver.session() as session:
            parameters = {
                'url': self.url,
                'title': self.title,
                'abstract': self.abstract,
                'content': self.content
            }
            query = """
                MERGE (n:WebResource {url: $url})
                SET n.title = $title, n.abstract = $abstract, n.content = $content
            """
            session.run(query, parameters=parameters)

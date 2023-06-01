import re
from html import unescape

import unicodedata
from bs4 import BeautifulSoup
from django.db import models


class WebResource(models.Model):
    url = models.URLField(max_length=2000, unique=True, verbose_name='URL')
    title = models.CharField(max_length=2000, verbose_name='Заголовок')
    abstract = models.TextField(verbose_name='Анотація')
    content = models.TextField(verbose_name='Вміст', blank=True)

    class Meta:
        verbose_name = 'Веб-ресурс'
        verbose_name_plural = 'Веб-ресурси'

    def __str__(self):
        return self.title

    @staticmethod
    def remove_html(text: str):
        soup = BeautifulSoup(text, 'html.parser')
        text_string = soup.get_text(separator=' ')
        s = unicodedata.normalize('NFKC', unescape(text_string))
        return re.sub(r'\s+', ' ', s)
    @property
    def content_without_html(self):
        return str(self.remove_html(self.content))

    def save(self, *args, **kwargs):
        if not self.abstract:
            self.abstract = self.remove_html(self.title)
            if self.content:
                self.abstract += ' ' + self.remove_html(self.content)
                self.abstract = " ".join(self.abstract.split(' ')[:128])

        super().save(*args, **kwargs)

        # create dense vector, add it to embeddings file and to faiss index
        # write_embeddings([self], 'wb+')
        # vector = bi_encoder.encode([self.abstract])[0]
        # text_index.add_with_ids(vector, [self.id])




from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer, token_filter

from articles.models import WebResource


@registry.register_document
class WebResourceDocument(Document):
    class Index:
        # Name of the Elasticsearch index
        name = 'web_resources'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 2,
                    'number_of_replicas': 0}

    title = fields.TextField(attr='title', analyzer='ukrainian')
    content = fields.TextField(attr='content', analyzer='ukrainian')
    url = fields.TextField(attr='url')

    class Django:
        model = WebResource  # The model associated with this Document

        queryset_pagination = 40

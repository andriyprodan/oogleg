from django.conf import settings
from elasticsearch import Elasticsearch

es_client = Elasticsearch(**settings.ELASTICSEARCH_DSL['default'])

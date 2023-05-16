from django.apps import AppConfig
from django.conf import settings
from elasticsearch_dsl import connections


class ArticlesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'articles'

from django.apps import AppConfig
from django.conf import settings
from elasticsearch_dsl import connections
import importlib
import inspect
from django.apps import apps
from elasticsearch_dsl import Document


def create_indexes():
    # Get all installed Django apps
    for app in apps.get_app_configs():
        # Get app module
        app_module = app.module.__name__
        # Find all modules with es_documents.py file in the app
        try:
            module = importlib.import_module(f"{app_module}.es_documents")
        except ModuleNotFoundError:
            continue
        # Iterate through all classes in the module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Check if class inherits from elasticsearch_dsl.Document
            if issubclass(obj, Document) and hasattr(obj, 'Index'):
                # Create index in the Elasticsearch
                obj.init(index=obj.Index.name)


    # not used

class DjangoEsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_es'

    # def ready(self):
    #     connections.configure(**settings.ELASTICSEARCH_DSL)
        # create_indexes()

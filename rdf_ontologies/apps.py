from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class CustomAdminConfig(AdminConfig):  # 1.
    default_site = 'rdf_ontologies.admin.CustomAdminSite'  # 2.
    # verbose_name = 'Веб-ресурси'  # 3.
    # name = 'rdf_ontologies_admin'  # 4.


class RdfOntologiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rdf_ontologies'

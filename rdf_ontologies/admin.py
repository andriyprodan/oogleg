from django.contrib.admin import AdminSite
from django.urls import path

from rdf_ontologies.views import OntologyPredicatesList, OntologyPredicatesAdd


class CustomAdminSite(AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('ontology_predicates/',
                self.admin_view((
                OntologyPredicatesList.as_view(admin_site=self))), name='ontology_predicates_list'),
            path('ontology_predicates/add',
                 self.admin_view((
                     OntologyPredicatesAdd.as_view(admin_site=self))), name='ontology_predicates_add'),

        ]
        return my_urls + urls



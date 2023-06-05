from django.contrib.admin import AdminSite
from django.urls import path

from rdf_ontologies.views import OntologyPredicatesList, OntologyPredicatesAdd, OntologyTagsList, OntologyTagsAdd, \
    OntologyClassesList, OntologyClassesAdd


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
            path('ontology_tags/',
                 self.admin_view((
                     OntologyTagsList.as_view(admin_site=self))), name='ontology_tags_list'),
            path('ontology_tags/add',
                 self.admin_view((
                     OntologyTagsAdd.as_view(admin_site=self))), name='ontology_tags_add'),
            path('ontology_classes/',
                 self.admin_view((
                     OntologyClassesList.as_view(admin_site=self))), name='ontology_classes_list'),
            path('ontology_classes/add',
                 self.admin_view((
                     OntologyClassesAdd.as_view(admin_site=self))), name='ontology_classes_add'),

        ]
        return my_urls + urls



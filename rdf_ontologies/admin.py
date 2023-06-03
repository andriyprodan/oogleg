from django.contrib.admin import AdminSite
from django.urls import path

from articles.views import OntologyPredicatesList


class CustomAdminSite(AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('ontology_predicates/',
                self.admin_view((
                OntologyPredicatesList.as_view(admin_site=self))), name='ontology_predicates'),
        ]
        return my_urls + urls



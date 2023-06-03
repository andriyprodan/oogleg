from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView
from rdflib import RDF, URIRef
from rdflib.plugins.sparql.parser import SelectQuery

from rdf_ontologies.RDF_graph import my_graph


class OntologyAdminView(PermissionRequiredMixin, TemplateView):
    admin_site = None
    template_name = 'articles/ontology_list.html'
    # superuser permissions
    permission_required = 'auth.is_superuser'

    def get_instances(self):
        raise NotImplementedError('You must implement get_instances method in your view class.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_nav_sidebar_enabled'] = True
        context.update(self.admin_site.each_context(self.request))
        context['instances'] = self.get_instances()
        return context

    def delete(self, objects_to_delete, *args, **kwargs):
        raise NotImplementedError('You must implement delete method in your view class.')

    def post(self, request, *args, **kwargs):
        objects_to_delete = request.POST.getlist('delete_checkbox')
#         check in graph if there is any subjects/predicates/objects to delete
        if objects_to_delete:
            sparql_query = f"""
            SELECT ?s ?p ?o
            WHERE {{
                ?s ?p ?o .
                FILTER (?p IN ({', '.join(['<' + s + '>' for s in objects_to_delete])}))
                }}"""
            results = my_graph.query(sparql_query)
            if results:
                return render(request, 'articles/are_you_sure.html', {
                    'objects_to_delete': results,
                    'objects_to_delete_count': len(results),
                    # 'objects_to_delete_type': 'predicate',
                    # 'objects_to_delete_plural': 'predicates',
                    **self.admin_site.each_context(self.request)
                })
        return self.delete(objects_to_delete, *args, **kwargs)





# Create your views here.
class OntologyPredicatesList(OntologyAdminView):
    def get_instances(self):
        return my_graph.subjects(RDF.type, RDF.Property)

    def delete(self, objects_to_delete, *args, **kwargs):
        return
        for obj in objects_to_delete:
            my_graph.remove((None, URIRef(obj), None))
        return self.get(self.request, *args, **kwargs)

    # template_name = 'articles/predicates_list.html'
    # superuser permissions

    # def post(self, request, *args, **kwargs):
    #     predicates_to_delete = request.POST.getlist('delete_checkbox')
    #     for predicate in predicates_to_delete:
    #         my_graph.remove((None, URIRef(predicate), None))
    #     return self.get(request, *args, **kwargs)

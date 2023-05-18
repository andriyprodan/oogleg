from django.contrib import admin
from rdflib import URIRef, Literal

from articles.models import WebResource
from oogleg import settings
from rdf_ontologies.RDF_graph import my_graph


# Register your models here.
@admin.register(WebResource)
class WebResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'abstract', 'url')
    search_fields = ('url', 'title', 'abstract')

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        if object_id and request.method == 'POST':
            url = WebResource.objects.get(pk=object_id).url
            my_graph.remove((URIRef(url), None, None))
            my_graph.remove((None, None, URIRef(url)))
            for key, value in request.POST.items():
                if key.startswith('predicate_objects_predicate_value-'):
                    predicate = value
                    number = key.rsplit('-', 1)[1]
                    object = request.POST.get(f'predicate_objects_object_value-{number}')
                    if not object:
                        continue
                    # if object is not URL
                    if not object.startswith('http'):
                        object = Literal(object)
                    else:
                        object = URIRef(object)
                    if predicate and object:
                        my_graph.add((URIRef(url), URIRef(predicate), object))
                elif key.startswith('subject_predicates_subject_value-'):
                    subject = value
                    number = key.rsplit('-', 1)[1]
                    predicate = request.POST.get(f'subject_predicates_predicate_value-{number}')
                    if not predicate:
                        continue
                    if not subject.startswith('http'):
                        subject = Literal(subject)
                    else:
                        subject = URIRef(subject)
                    if subject and predicate:
                        my_graph.add((URIRef(subject), URIRef(predicate), URIRef(url)))
            my_graph.serialize(destination=str(settings.BASE_DIR / "ontology.ttl"), format="turtle")

        if object_id:
            url = WebResource.objects.get(pk=object_id).url

            extra_context['all_predicates'] = my_graph.get_oogleg_properties()
            extra_context['subject_predicates'] = my_graph.subject_predicates(object=URIRef(url))
            extra_context['predicate_objects'] = my_graph.predicate_objects(subject=URIRef(url))

        return super().changeform_view(request, object_id, extra_context=extra_context)
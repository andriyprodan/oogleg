import spacy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from rdflib import RDF, URIRef
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from articles.models import WebResource
from rdf_ontologies.RDF_graph import my_graph
from rdf_ontologies.constants import oogleg_voc
from rdf_ontologies.forms import OntologyPredicatesAddForm

nlp = spacy.load("uk_core_news_trf")


# Create your views here.
class GetConnections(APIView):
    def get(self, request, **kwargs):
        id = kwargs['id']
        try:
            web_resource = WebResource.objects.get(pk=id)
        except WebResource.DoesNotExist:
            return Response({'error': 'Web resource does not exist.'}, status=404)

        subjects = my_graph.triples((None, None, URIRef(web_resource.url)))
        objects = my_graph.triples((URIRef(web_resource.url), None, None))
        subjects_list = []
        for s, p, o in subjects:
            data = {'subject': {}, 'predicate': str(p).split('https://oogleg.co/vocabulary/')[1].replace('_', ' ')}
            if not isinstance(s, URIRef):
                data['subject']['title'] = str(s)
            else:
                data['subject']['url'] = str(s)
                try:
                    web_resource = WebResource.objects.get(url=str(s))
                    data['subject']['title'] = web_resource.title
                except WebResource.DoesNotExist:
                    data['subject']['title'] = data['object']['url']

            subjects_list.append(data)

        objects_list = []
        for s, p, o in objects:
            # if object is not URL
            data = {'object': {}, 'predicate': str(p).split('https://oogleg.co/vocabulary/')[1].replace('_', ' ')}
            if not isinstance(o, URIRef):
                data['object']['title'] = str(o)
            else:
                data['object']['url'] = str(o)
                try:
                    web_resource = WebResource.objects.get(url=str(o))
                    data['object']['title'] = web_resource.title
                except WebResource.DoesNotExist:
                    data['object']['title'] = data['object']['url']

            objects_list.append(data)

        return Response({
            'subjects': subjects_list,
            'objects': objects_list,
        })


class GetTextWithMatchedPredicates(APIView):
    permission_classes = []
    authentication_classes = [SessionAuthentication]

    def get_predicates(self, text):
        doc = nlp(text)

        # Define the relationship patterns in Ukrainian
        oogleg_predicates = my_graph.get_oogleg_properties()
        formatted_predicates = [str(predicate).split('https://oogleg.co/vocabulary/')[1].replace('_', ' ') for predicate
                                in
                                oogleg_predicates]
        patterns = [
            [{"LOWER": predicate_word} for predicate_word in predicate.split(' ')] for predicate in formatted_predicates
            #     verbs patterns
        ]
        patterns.append([{"POS": "VERB"}])

        matcher = spacy.matcher.Matcher(nlp.vocab)
        for pattern in patterns:
            matcher.add("RELATIONSHIPS", [pattern], on_match=None)

        # Add the patterns to the spaCy matcher
        triples = []
        matches = reversed(matcher(doc))
        highlighted_text = text
        changes = []
        for match_id, start, end in matches:
            #             highlight oogleg_predicates in red using html and highlight verbs in <b> using html and modify initial text
            original_text = span_text = doc[start:end].text
            # span_start = doc[start].idx
            # span_end = doc[end - 1].idx + len(doc[end - 1].text)
            # Highlight Oogleg predicates in red using <span> with a CSS class
            if span_text in formatted_predicates:
                span_text = f'<span style="color: red;">{span_text}</span>'
            # Highlight verbs using <b> tags
            if doc[start:end].root.pos_ == "VERB":
                span_text = f'<b>{span_text}</b>'
            # Replace the original span with the highlighted span in the text
            changes.append((original_text, span_text))

        changes = list(set(changes))
        # order changes by <span style="color: red;">
        changes.sort(key=lambda x: x[0] in formatted_predicates, reverse=True)

        for original_text, span_text in changes:
            highlighted_text = highlighted_text.replace(original_text, span_text)

        return highlighted_text

    def post(self, request, **kwargs):
        # Load the spaCy Ukrainian model

        # Example texts in Ukrainian
        title = request.data.get('title')
        highlighted_title = self.get_predicates(title)
        content = request.data.get('content')
        highlighted_content = self.get_predicates(content)

        return Response({
            'title': highlighted_title,
            'content': highlighted_content,
        })


class OntologyAdminListView(PermissionRequiredMixin, TemplateView):
    admin_site = None
    template_name = 'rdf_ontologies/ontology_list.html'
    # superuser permissions
    permission_required = 'auth.is_superuser'

    def get_instances(self):
        raise NotImplementedError('You must implement get_instances method in your view class.')

    def get_triples_query(self, instances_to_delete):
        raise NotImplementedError('You must implement get_triples_query method in your view class.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.admin_site.each_context(self.request))
        context['instances'] = self.get_instances()
        return context

    def delete(self, instances_to_delete, *args, **kwargs):
        for obj in instances_to_delete:
            my_graph.remove_comletely(resource=URIRef(obj))
        my_graph.serialize()
        return self.get(self.request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        instances_to_delete = request.POST.getlist('instances_to_delete')
        #         check in graph if there is any subjects/predicates/objects to delete
        if instances_to_delete:
            sparql_query = self.get_triples_query(instances_to_delete)
            triples_to_delete = my_graph.query(sparql_query)
            if triples_to_delete:
                if 'confirm_delete' in request.POST:
                    return self.delete(instances_to_delete, *args, **kwargs)
                else:
                    return render(request, 'rdf_ontologies/are_you_sure.html', {
                        'triples_to_delete': triples_to_delete,
                        'triples_to_delete_count': len(triples_to_delete),
                        'instances_to_delete': instances_to_delete,
                        # 'instances_to_delete_type': 'predicate',
                        # 'instances_to_delete_plural': 'predicates',
                        **self.admin_site.each_context(self.request)
                    })
            return self.delete(instances_to_delete, *args, **kwargs)
        return self.get(request, *args, **kwargs)


class OntologyAdminAddView(PermissionRequiredMixin, TemplateView):
    admin_site = None
    template_name = 'rdf_ontologies/ontology_add.html'
    permission_required = 'auth.is_superuser'

    def create_instance(self, predicate):
        raise NotImplementedError('You must implement create_instance method in your view class.')

    def get_form_class(self):
        raise NotImplementedError('You must implement get_form_class method in your view class.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.admin_site.each_context(self.request))
        context['form'] = self.get_form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form_class()(request.POST)
        if form.is_valid():
            self.create_instance(form)
            return redirect('admin:ontology_predicates_list')
        return render(request, self.template_name, {
            'form': form,
            **self.admin_site.each_context(self.request)
        })


# Create your views here.
class OntologyPredicatesList(OntologyAdminListView):
    def get_instances(self):
        return my_graph.subjects(RDF.type, RDF.Property)

    def get_triples_query(self, instances):
        return f"""
            SELECT ?s ?p ?o
            WHERE {{
                ?s ?p ?o .
                FILTER (?p IN ({', '.join(['<' + s + '>' for s in instances])}))
                }}"""


class OntologyPredicatesAdd(OntologyAdminAddView):
    def get_form_class(self):
        return OntologyPredicatesAddForm

    def create_instance(self, form):
        predicate = form.cleaned_data['predicate_name']
        # create predicate

        my_graph.add((URIRef(oogleg_voc + predicate), RDF.type, RDF.Property))
        my_graph.serialize()











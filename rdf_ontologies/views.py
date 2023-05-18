from django.shortcuts import render
from rdflib import URIRef
from rest_framework.response import Response
from rest_framework.views import APIView
import spacy

from articles.models import WebResource
from rdf_ontologies.RDF_graph import my_graph

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
        matches = matcher(doc)
        highlighted_text = text
        for match_id, start, end in matches:
            #             highlight oogleg_predicates in red using html and highlight verbs in <b> using html and modify initial text
            span_text = doc[start:end].text
            span_start = doc[start].idx
            span_end = doc[end - 1].idx + len(doc[end - 1].text)
            # Highlight Oogleg predicates in red using <span> with a CSS class
            if span_text in formatted_predicates:
                span_text = f'<span style="color: red;">{span_text}</span>'
            # Highlight verbs using <b> tags
            if doc[start:end].root.pos_ == "VERB":
                span_text = f'<b>{span_text}</b>'
            # Replace the original span with the highlighted span in the text
            highlighted_text = highlighted_text[:span_start] + span_text + highlighted_text[span_end:]

        return highlighted_text

    def get(self, request, **kwargs):
        # Load the spaCy Ukrainian model

        # Example texts in Ukrainian
        title = request.GET.get('title')
        highlighted_title = self.get_predicates(title)
        content = request.GET.get('content')
        highlighted_content = self.get_predicates(content)

        return Response({
            'title': highlighted_title,
            'content': highlighted_content,
        })

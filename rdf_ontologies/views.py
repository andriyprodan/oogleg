from django.shortcuts import render
from rdflib import URIRef
from rest_framework.response import Response
from rest_framework.views import APIView

from articles.models import WebResource
from rdf_ontologies.RDF_graph import my_graph


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

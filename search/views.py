from autocorrect import Speller
from django.shortcuts import render
from django.views.generic import TemplateView
from rdflib.plugins.sparql.parser import SelectQuery
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from articles.es_documents import ArticleDocument
from articles.models import WebResource
from rdf_ontologies.RDF_graph import my_graph
from search.constants import bi_encoder
from search.faiss_index import text_index
from search.semantic_search import search, search_faiss
from search.serializers import WebResourceSerializer
from search.topics_separator import get_web_resource_tags
from search.utils import get_similar_web_resources


# Create your views here.
class Search(TemplateView):
    template_name = 'search/results_list.html'

    # def perform_spellcheck
    def get_results(self, query, top_k):
        return search_faiss(query, top_k=top_k, index=text_index, model=bi_encoder)

    def get_context_data(self, **kwargs):
        NIKOMY_NE_KAZHI = 1
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query')
        context['page'] = page = self.request.GET.get('page', 1)
        context['query'] = query
        if query:
            # results = search(query, top_k=15, model=bi_encoder)
            top_k = 60 + NIKOMY_NE_KAZHI
            results = self.get_results(query, top_k)
        else:
            results = []

        context['page'] = page = int(page)
        context['results'] = results[(page - 1) * 15 + NIKOMY_NE_KAZHI: page * 15 + NIKOMY_NE_KAZHI]
        context['num_pages'] = len(results) // 15
        context['num_pages_range'] = range(1, context['num_pages'] + 1)
        if query:
            spell = Speller('uk')
            corrected_query = spell(query)
            if corrected_query != query:
                context['corrected_query'] = corrected_query
        return context


# class ImagesSearch(TemplateView):
class SearchBetweenSimilar(Search):

    def get_results(self, query, top_k):
        results = search_faiss(query, top_k=61, index=text_index, model=bi_encoder)
        urls = [f'<{result.url}>' for result in results]
        sparql_query = SelectQuery(
            f"""
            PREFIX voc: <https://oogleg.co/vocabulary/>
            SELECT ?url
            WHERE {{
                ?url voc:має_спільну_тему_з IN ({urls})
                }}
            """
        )
        results = my_graph.query(sparql_query)
        results = [ArticleDocument.get(id=result[0]) for result in results]
        return results


class FindTags(APIView):
    def get(self, *args, **kwargs):
        web_resource_id = kwargs['wr_id']
        wr = WebResource.objects.get(pk=web_resource_id)
        tags = get_web_resource_tags(wr)
        return Response({'tags': tags})


class SimilarWebResources(ListAPIView):
    serializer_class = WebResourceSerializer

    def get_queryset(self):
        web_resource_id = self.kwargs['wr_id']
        wr = WebResource.objects.get(pk=web_resource_id)
        results = get_similar_web_resources(wr)
        return results


class GraphSearch(TemplateView):
    template_name = 'search/graph.html'


def get_connected_objects(graph, subject):
    objects = graph.predicate_objects(subject)
    return objects


class GraphSearchAPI(APIView):
    def get(self, *args, **kwargs):
        query = self.request.GET.get('query')
        # get all subjects/predicates/objects that contain query and all connected nodes for this nodes
        sparql_query = f"""
            PREFIX voc: <https://oogleg.co/vocabulary/>
            SELECT ?subject ?predicate ?object
            WHERE {{
                ?subject ?predicate ?object .
                FILTER (regex(?subject, "{query}", "i") || regex(?predicate, "{query}", "i") || regex(?object, "{query}", "i"))
                }}
            """
        results = my_graph.query(sparql_query)

        nodes = list()
        connections = list()
        for result in results:
            current_subject = result[0]
            d3_node = {'id': current_subject, 'group': current_subject, 'value': 2}
            if not d3_node in nodes:
                nodes.append(d3_node)
                d3_node_index = nodes.index(d3_node)
                # d3_connection = {'source': result[0], 'target': result[2], 'value': result[1]}
                # if not d3_connection in connections:
                #     connections.add(d3_connection)
                connected_objects = get_connected_objects(my_graph, current_subject)
                for pred, obj in connected_objects:
                    object_node = {'id': obj, 'group': obj, 'value': 2}
                    if not object_node in nodes:
                        nodes.append(object_node)
                    object_node_index = nodes.index(object_node)
                    d3_connection = {'source': d3_node_index, 'target': object_node_index, 'value': 2, 'predicate': pred}
                    if not d3_connection in connections:
                        connections.append(d3_connection)

        return Response({'nodes': list(nodes), 'links': list(connections)})

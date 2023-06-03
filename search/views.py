from autocorrect import Speller
from django.shortcuts import render
from django.views.generic import TemplateView
from rdflib.plugins.sparql.parser import SelectQuery

from articles.es_documents import ArticleDocument
from rdf_ontologies.RDF_graph import my_graph
from search.constants import bi_encoder
from search.faiss_index import text_index
from search.semantic_search import search, search_faiss


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





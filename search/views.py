from django.shortcuts import render
from django.views.generic import TemplateView

from articles.es_documents import ArticleDocument
from search.constants import bi_encoder
from search.faiss_index import text_index
from search.semantic_search import search, search_faiss


# Create your views here.
class Search(TemplateView):
    template_name = 'search/results_list.html'

    # def perform_spellcheck

    def get_context_data(self, **kwargs):
        NIKOMY_NE_KAZHI = 1
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query')
        context['page'] = page = self.request.GET.get('page', 1)
        context['query'] = query
        if query:
            # results = search(query, top_k=15, model=bi_encoder)
            top_k = 60 + NIKOMY_NE_KAZHI
            results = search_faiss(query, top_k=top_k, index=text_index, model=bi_encoder)
        else:
            results = []

        context['page'] = page = int(page)
        context['results'] = results[(page - 1) * 15 + NIKOMY_NE_KAZHI: page * 15 + NIKOMY_NE_KAZHI]
        context['num_pages'] = len(results) // 15
        context['num_pages_range'] = range(1, context['num_pages'] + 1)
        return context


# class ImagesSearch(TemplateView):
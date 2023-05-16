from django.shortcuts import render
from django.views.generic import TemplateView

from articles.es_documents import ArticleDocument
from search.constants import bi_encoder
from search.faiss_index import text_index
from search.semantic_search import search


# Create your views here.
class Search(TemplateView):
    template_name = 'search/results_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query')
        if query:
            results = search(query, top_k=15, index=text_index, model=bi_encoder)
            # results = ArticleDocument.search().query('match', abstract=query).execute()
        else:
            results = []
        context['results'] = results
        return context


# class ImagesSearch(TemplateView):
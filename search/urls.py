from django.urls import path

from search.views import Search, SearchBetweenSimilar, FindTags, SimilarWebResources, GraphSearch, GraphSearchAPI

app_name = 'search'
urlpatterns = [
    path('', Search.as_view(), name='index'),
    path('graph_search/', GraphSearch.as_view(), name='graph_search'),
    path('similar_search/', SearchBetweenSimilar.as_view(), name='similar_search'),
    path('<int:wr_id>/find_wr_tags/', FindTags.as_view(), name='find_tags'),
    path('<int:wr_id>/similar_web_resources/', SimilarWebResources.as_view(), name='similar_web_resources'),
    path('api/graph_search/', GraphSearchAPI.as_view(), name='graph_search_api'),
]
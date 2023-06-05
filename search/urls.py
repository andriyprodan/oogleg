from django.urls import path

from search.views import Search, SearchBetweenSimilar, FindTags

app_name = 'search'
urlpatterns = [
    path('', Search.as_view(), name='index'),
    path('similar_search/', SearchBetweenSimilar.as_view(), name='similar_search'),
    path('<int:wr_id>/find_wr_tags/', FindTags.as_view(), name='find_tags'),
]
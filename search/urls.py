from django.urls import path

from search.views import Search, SearchBetweenSimilar

app_name = 'search'
urlpatterns = [
    path('', Search.as_view(), name='index'),
    path('similar_search/', SearchBetweenSimilar.as_view(), name='similar_search'),
]
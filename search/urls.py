from django.urls import path

from search.views import Search, Graph

app_name = 'search'
urlpatterns = [
    path('', Search.as_view(), name='index'),
    path('graph', Graph.as_view(), name='graph'),
]
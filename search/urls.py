from django.urls import path

from search.views import Search, Graph

urlpatterns = [
    path('', Search.as_view(), name='index'),
    path('graph', Graph.as_view(), name='graph'),
]
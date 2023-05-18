from django.urls import path, include

from rdf_ontologies.views import GetConnections

urlpatterns = [
    path('admin/', include([
        path('', include('search.urls'), name='admin_base'),
    ])),
    path('api/', include([
        path('<int:id>/get_graph_connections/', GetConnections.as_view(), name='get_graph_connections'),
    ])),
]
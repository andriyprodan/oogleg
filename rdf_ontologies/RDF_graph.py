from django.conf import settings
from rdflib import Graph, URIRef
from rdflib.namespace import RDFS, SKOS


class MyGraph(Graph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parse(str(settings.BASE_DIR / "ontology.ttl"), format="turtle")


my_graph = MyGraph()

import rdflib
from django.conf import settings
from rdflib import Graph, URIRef, RDF
from rdflib.extras.infixowl import Property
from rdflib.namespace import RDFS, SKOS, Namespace


class MyGraph(Graph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parse(str(settings.BASE_DIR / "ontology.ttl"), format="turtle")

    def get_oogleg_properties(self):
        voc = Namespace("https://oogleg.co/vocabulary/")

        # Get all properties
        properties = []
        for s, p, o in self.triples((None, RDF.type, RDF.Property)):
            if str(s).startswith(str(voc)):
                properties.append(str(s))
        return properties

    def serialize(self, **kwargs) -> bytes:
        return super().serialize(destination=str(settings.BASE_DIR / "ontology.ttl"), format="turtle", **kwargs)

    def remove_comletely(self, resource):
        self.remove((resource, None, None))
        self.remove((None, resource, None))
        self.remove((None, None, resource))



my_graph = MyGraph()

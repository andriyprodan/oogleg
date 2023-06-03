import spacy
from django.core.management import BaseCommand
from rdflib import URIRef, RDF

from rdf_ontologies.RDF_graph import my_graph
from rdf_ontologies.constants import oogleg_voc


class Command(BaseCommand):

    def handle(self, *args, **options):
        so = my_graph.subject_objects(predicate=URIRef(f'{oogleg_voc}має_тег'))
        i = 0
        for _, o in so:
            my_graph.add((o, RDF.type, URIRef(oogleg_voc + 'Тег')))
            i += 1
            if i % 500 == 0:
                my_graph.serialize()




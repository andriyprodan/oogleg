import spacy
from django.core.management import BaseCommand
from rdflib import URIRef

from rdf_ontologies.RDF_graph import MyGraph
from rdf_ontologies.constants import oogleg_voc


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('reduced_topics.txt', 'r', encoding='utf-8') as f:
            reduced_topics = set(f.read().split('\n') )
        my_graph = MyGraph()
        for rt in reduced_topics:
            tag_url = f'{oogleg_voc}tag/{rt}'
            my_graph.remove((URIRef(tag_url), None, None))
            my_graph.remove((None, None, URIRef(tag_url)))
        my_graph.serialize()



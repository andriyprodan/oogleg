import spacy
from django.core.management import BaseCommand
from rdflib import URIRef, RDF, Literal

from articles.models import WebResource
from rdf_ontologies.RDF_graph import my_graph
from rdf_ontologies.constants import oogleg_voc


class Command(BaseCommand):

    def handle(self, *args, **options):
        i = 0
        for wr in WebResource.objects.all():
            my_graph.add((URIRef(wr.url), RDF.type, URIRef(oogleg_voc + 'Веб_Ресурс')))
            my_graph.add((URIRef(wr.url), URIRef(oogleg_voc + 'має_заголовок'), Literal(wr.title)))
            # my_graph.add((URIRef(wr.url), URIRef(oogleg_voc + 'має_анотацію'), Literal(wr.abstract)))

            i += 1
            if i % 500 == 0:
                print(f'processed {i} web resources')
                my_graph.serialize()








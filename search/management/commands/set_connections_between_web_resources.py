from django.core.management import BaseCommand
import numpy as np
from rdflib import URIRef, RDF

from rdf_ontologies.RDF_graph import my_graph
from rdf_ontologies.constants import oogleg_voc
from search.faiss_index import text_index, ids_data
from articles.models import WebResource
from search.utils import encode_string


class Command(BaseCommand):

    def handle(self, *args, **options):
        i = 0
        for web_resourse in WebResource.objects.all():
            # print('-' * 100)
            # print(web_resourse.abstract)
            target_vector = encode_string(web_resourse.abstract)
            target_vector = target_vector.cpu()

            # Step 2: Convert the tensor to a NumPy array
            target_vector = target_vector.numpy()
            distances, indices = text_index.search(np.array([target_vector]), 3)
            for i in indices[0]:
                db_id = ids_data['db_ids'][i]
                try:
                    other_web_resource = WebResource.objects.get(id=db_id)
                    # print(other_web_resource.abstract)
                except:
                    continue

#                 check if there is a common tags between the two web resources in the RDF graph
                common_tags = set()
                first_wr_connections = my_graph.objects(URIRef(other_web_resource.url), URIRef(f'{oogleg_voc}має_тег'))
                second_wr_connections = my_graph.objects(URIRef(web_resourse.url), URIRef(f'{oogleg_voc}має_тег'))
                for first_wr_connection in first_wr_connections:
                    for second_wr_connection in second_wr_connections:
                        if first_wr_connection == second_wr_connection:
                            common_tags.add(first_wr_connection)

                if len(common_tags) > 0:
                    # print('common tags:')
                    # print(common_tags)

                    my_graph.add((URIRef(web_resourse.url), URIRef(f'{oogleg_voc}має_спільну_тему_з'), URIRef(other_web_resource.url)))
                    my_graph.add((URIRef(other_web_resource.url), URIRef(f'{oogleg_voc}має_спільну_тему_з'), URIRef(web_resourse.url)))

            i += 1
            if i % 500 == 0:
                print(f'processed {i} web resources')
                my_graph.serialize()






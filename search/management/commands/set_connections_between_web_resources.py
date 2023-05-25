from django.core.management import BaseCommand
import numpy as np

from search.faiss_index import text_index, ids_data
from articles.models import WebResource
from search.utils import encode_string


class Command(BaseCommand):

    def handle(self, *args, **options):
        for web_resourse in WebResource.objects.all()[:10]:
            print('-' * 100)
            print(web_resourse.abstract)
            target_vector = encode_string(web_resourse.abstract)
            target_vector = target_vector.cpu()

            # Step 2: Convert the tensor to a NumPy array
            target_vector = target_vector.numpy()
            distances, indices = text_index.search(np.array([target_vector]), 5)
            for i in indices[0]:
                db_id = ids_data['db_ids'][i]
                try:
                    wr = WebResource.objects.get(id=db_id)
                    print(wr.abstract)
                except:
                    continue



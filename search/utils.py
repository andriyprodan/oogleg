import concurrent.futures
import numpy as np
import pandas as pd

from articles.models import WebResource
from search.constants import bi_encoder
from search.faiss_index import ids_data, text_index
from search.serializers import WebResourceSerializer
from search.topics_separator import get_web_resource_tags


# not used
def convert_to_dataframe(data):
    return pd.DataFrame([{
        'abstract': data['abstracts'][i],
        'title': data['titles'][i],
        'url': data['urls'][i],
    } for i in range(len(data['abstracts']))])


def encode_string(text):
    return bi_encoder.encode(text, convert_to_tensor=True)


def get_similar_web_resources(web_resource: WebResource):


    target_vector = encode_string(web_resource.abstract)
    target_vector = target_vector.cpu()
    target_vector = target_vector.numpy()
    distances, indices = text_index.search(np.array([target_vector]), 10)
    wr_tags = get_web_resource_tags(web_resource)
    similar_wrs = []

    def find_similar_web_resources(other_wr):
        other_wr_tags = get_web_resource_tags(other_wr)
        if bool(set(wr_tags) & set(other_wr_tags)):
            similar_wrs.append(other_wr)

        # return similar_wrs

    # Create a ThreadPoolExecutor with the desired number of threads
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

    # List to store the future objects
    futures = []

    # Iterate over your web resources
    for i in indices[0]:
        id = ids_data['db_ids'][i]
        wr = WebResource.objects.get(id=id)

        future = executor.submit(find_similar_web_resources, wr)
        futures.append(future)

    # List to store the results
    results = []

    # Retrieve the results from the futures as they become available
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
    #     results.append(result)

    return similar_wrs
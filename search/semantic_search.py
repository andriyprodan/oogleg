import time

import numpy as np
import torch
from sentence_transformers import util

from articles.models import WebResource
from search.faiss_index import ids_data


def fetch_web_resource_info(dataframe_idx):
    db_id = ids_data['db_ids'][dataframe_idx]

    return WebResource.objects.get(id=db_id)


def search_faiss(query, top_k, index, model):
    t = time.time()
    query_vector = model.encode([query])
    top_k = index.search(query_vector, top_k)
    print('>>>> Results in Total Time: {}'.format(time.time() - t))
    top_k_ids = top_k[1].tolist()[0]
    top_k_ids = list(np.unique(top_k_ids))
    results = [fetch_web_resource_info(idx) for idx in top_k_ids]
    return results


def search(query, top_k, model):
    t = time.time()
    query_vector = model.encode(query, convert_to_tensor=True).to(model.device)
    tensor_data = torch.tensor(ids_data['embeddings'], device=model.device)
    cos_scores = util.cos_sim(query_vector, tensor_data)[0]
    top_results = torch.topk(cos_scores, k=top_k)
    print('>>>> Results in Total Time: {}'.format(time.time() - t))
    # for score, idx in zip(top_results[0], ):
    #     print(ids_data['ids'][idx], "(Score: {:.4f})".format(score))
    # top_k_ids = top_k[1].tolist()[0]
    # top_k_ids = list(np.unique(top_k_ids))
    results = [fetch_web_resource_info(idx) for idx in top_results[1]]
    return results

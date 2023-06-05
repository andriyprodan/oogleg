from sentence_transformers import SentenceTransformer

trained_model_name = 'trained_paraphrase-multilingual-mpnet-base-v2'
model_name = 'paraphrase-multilingual-mpnet-base-v2'


# check if model exists locally, if not download and save
def get_encoder(device):
    try:
        return SentenceTransformer(trained_model_name, device=device)
    except:
        bi_encoder = SentenceTransformer(model_name, device=device)
        bi_encoder.save(trained_model_name)
        return SentenceTransformer(trained_model_name, device=device)


# We use the Bi-Encoder to encode all passages, so that we can use it with semantic search
# bi_encoder = get_encoder('cuda')
# bi_encoder.max_seq_length = 256  # Truncate long passages to 256 tokens
bi_encoder = None

max_corpus_size = 100000

embedding_size = 768  # Size of embeddings
top_k_hits = 32  # Output k hits

# Defining our FAISS index
# Number of clusters used for faiss. Select a value 4*sqrt(N) to 16*sqrt(N) - https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index
n_clusters = 1024

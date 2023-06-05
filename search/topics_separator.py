import spacy
from autocorrect import Speller
from django.conf import settings
from django.core.management import BaseCommand
from rdflib import URIRef, Literal, RDF
from top2vec import Top2Vec
from torchvision.datasets import voc

from articles.models import WebResource
from rdf_ontologies.RDF_graph import my_graph
from rdf_ontologies.constants import oogleg_voc

nlp = spacy.load("uk_core_news_trf")

with open('reduced_topics.txt', 'r', encoding='utf-8') as f:
    reduced_topics = set(f.read().split('\n'))

try:
    topics_model = Top2Vec.load("top2vec_model.bin")
except:
    documents = []
    document_ids = []
    for wr in WebResource.objects.all():
        document_ids.append(wr.id)
        abstract = wr.content_without_html
        # leave only letters, numbers, spaces and dots for abstracts
        # abstract = ''.join([c for c in abstract if c.isalpha() or c.isdigit() or c.isspace() or c == '.'])
        # abstract = ' '.join(abstract.split(' ')[:128])
        documents.append(abstract)
    umap_args = {
        'n_neighbors': 10,
        'n_components': 5,
        'metric': 'cosine',
        'random_state': 42
    }

    hdbscan_args = {
        'min_cluster_size': 10,
        'min_samples': 5,
        'metric': 'euclidean',
        'cluster_selection_method': 'eom'
    }
    topics_model = Top2Vec(documents=documents, document_ids=document_ids, speed='deep-learn', workers=8, min_count=0,
                    embedding_model='distiluse-base-multilingual-cased',
                    # embedding_model='paraphrase-multilingual-MiniLM-L12-v2',
                    umap_args=umap_args, hdbscan_args=hdbscan_args)
    topics_model.min_topic_size = 200
    topics_model.save("top2vec_model.bin")


spell = Speller('uk')

def get_corrected_topics(topic_words):
    corrected = spell(' '.join(topic_words))
    corrected = spell.existing(corrected.split(' '))
    corrected = spell(' '.join(corrected))
    doc = nlp(corrected)
    nouns = set([token.lemma_ for token in doc if token.pos_ == "NOUN" and 'Case=Nom' in token.morph])
    filtered = [word for word in nouns if word not in reduced_topics]
    return filtered


def get_web_resource_tags(wr: WebResource):
    doc_topics, doc_dist, topic_words, topic_word_scores = topics_model.get_documents_topics(doc_ids=[wr.id])
    current_topic_words = topic_words[0]
    filtered = get_corrected_topics(current_topic_words)
    return filtered

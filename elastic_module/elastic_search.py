# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch
from gensim.models import Word2Vec
from dotenv import load_dotenv
import numpy as np
import os

load_dotenv()

ELASTIC_CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")
ELASTIC_USERNAME = os.getenv("ELASTIC_USERNAME")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")

word_model = Word2Vec.load("w2v_custom_from_db.model")

es = Elasticsearch(
    cloud_id=ELASTIC_CLOUD_ID, basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD)
)


def search_articles(query):
    """
    Elasticsearch sonuçlarını getir.
    """
    try:
        response = es.search(
            index="wikipedia",
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title", "text"],
                        "type": "best_fields",
                    }
                },
                "size": 5,
            },
        )

        return [
            {
                "title": hit["_source"]["title"],
                "url": hit["_source"].get("url", "#"),
                "text": hit["_source"]["text"][:200] + "...",
            }
            for hit in response["hits"]["hits"]
        ]
    except Exception as e:
        print(f"Error during search: {e}")
        return []


def find_synonyms(query):
    """
    Word2Vec modeliyle eş anlamlı kelimeleri bul.
    """
    tokens = query.split()
    vectors = [word_model.wv[word] for word in tokens if word in word_model.wv]
    if not vectors:
        return []

    avg_vector = np.mean(vectors, axis=0)
    return [word for word, _ in word_model.wv.similar_by_vector(avg_vector)]


def fusion_search(query):
    """
    Word2Vec ve Elasticsearch sonuçlarını birleştir.
    """
    elastic_results = search_articles(query)
    synonyms = find_synonyms(query)

    return {"elastic": elastic_results, "synonyms": synonyms}

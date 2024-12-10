# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, jsonify
from gensim.models import Word2Vec
import numpy as np
from elastic_search import search_articles


app = Flask(__name__)

word_model = Word2Vec.load("w2v_custom_from_db.model")

def get_vector_for_multiple_words(words):
    """
    Çoklu kelimeler için Word2Vec vektörünü hesaplar.
    Kelimelerin ortalama vektörünü döndürür.
    """
    word_vectors = []
    for word in words:
        if word in word_model.wv: 
            word_vectors.append(word_model.wv[word])
    
    if word_vectors:  
        return np.mean(word_vectors, axis=0)
    else:
        return None  

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")  

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "")
    results = search_articles(query)
    return jsonify(results)

@app.route("/word2vec", methods=["GET"])
def word2vec():
    query = request.args.get("query", "").lower() 
    synonyms = []

    if query:
        query_tokens = query.split()
        query_vector = get_vector_for_multiple_words(query_tokens)
        
        if query_vector is not None:
            try:
                similar_words = word_model.wv.similar_by_vector(query_vector, topn=10)
                synonyms = [word for word, _ in similar_words]
            except KeyError:
                synonyms = []

    return jsonify(synonyms)

if __name__ == "__main__":
    app.run(debug=True)

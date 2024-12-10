import pymongo
import string
from gensim.models import Word2Vec
from TurkishStemmer import TurkishStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize
from dotenv import load_dotenv
import numpy as np
import os

load_dotenv()

MONGO_DB_URL = os.getenv("DATABASE_URL").replace(
    "<db_password>", os.getenv("DATABASE_PASSWORD")
)
client = pymongo.MongoClient(MONGO_DB_URL)
db = client["wikipedia"]
collection = db["wikipedia_tr"]

stemmer = TurkishStemmer()

tfidf_vectorizer = TfidfVectorizer()

def clean_and_stem(text):
    text = text.translate(str.maketrans("", "", string.punctuation)).lower()
    tokens = word_tokenize(text)
    return [stemmer.stem(token) for token in tokens]

def fetch_and_train_model():
    """
    Veritabanındaki belgelerle Word2Vec modelini eğitir.
    """
    print("Veri temizleniyor ve model eğitiliyor...")
    corpus = []

    for document in collection.find({}, {"text": 1}):
        text = document.get("text", "")
        tokens = clean_and_stem(text)
        corpus.append(tokens)

    model = Word2Vec(
        sentences=corpus,
        vector_size=100,
        window=5,
        min_count=7,
        workers=4,
        epochs=10,
    )

    model.save("w2v_custom_from_db.model")
    print("Model eğitildi ve kaydedildi.")
    return model

def analyze_query(query, model, top_n=5):
    """
    Sorguyu başlıklara ve içeriğe göre analiz eder.
    """
    query_tokens = clean_and_stem(query)
    print(f"Temizlenmiş sorgu: {query_tokens}")
    
    relevant_docs = []
    for document in collection.find({}, {"title": 1, "text": 1}):
        title = document.get("title", "")
        content = document.get("text", "")
        
        title_tokens = clean_and_stem(title)
        if any(q in title_tokens for q in query_tokens):
            relevant_docs.append({
                "title": title,
                "content": content,
                "stemmed_title": title_tokens,
            })
    
    if relevant_docs:
        corpus = [doc["content"] for doc in relevant_docs]
        tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
        
        query_vector = tfidf_vectorizer.transform([" ".join(query_tokens)])
        scores = np.dot(tfidf_matrix, query_vector.T).toarray().flatten()
        
        for i, doc in enumerate(relevant_docs):
            doc["score"] = scores[i]
        
        sorted_docs = sorted(relevant_docs, key=lambda x: x["score"], reverse=True)
        return sorted_docs[:top_n]
    else:
        return []

if __name__ == "__main__":
    if not os.path.exists("w2v_custom_from_db.model"):
        word_model = fetch_and_train_model()
    else:
        print("Eğitilmiş model yükleniyor...")
        word_model = Word2Vec.load("w2v_custom_from_db.model")

    while True:
        query = input("Arama yapmak için kelime veya kelimeler girin (çıkmak için 'q'): ").strip()
        if query.lower() == 'q':
            break
        
        results = analyze_query(query, word_model)
        if results:
            print("Sonuçlar:")
            for idx, res in enumerate(results, start=1):
                print(f"\n#{idx}:")
                print(f"Başlık: {res['title']}")
                print(f"Skor: {res['score']:.4f}")
        else:
            print("Alakalı bir sonuç bulunamadı.")

import numpy as np
from gensim.models import Word2Vec
from TurkishStemmer import TurkishStemmer
from nltk.tokenize import word_tokenize

stemmer = TurkishStemmer()

model_path = "w2v_custom_from_db.model"
try:
    model = Word2Vec.load(model_path)
    print(f"Model başarıyla yüklendi: {model_path}")
except FileNotFoundError:
    print(f"Model dosyası bulunamadı: {model_path}. Lütfen önce modeli eğitin.")
    exit()

def get_vector_for_multiple_words(model, words):
    """
    Çoklu kelimeler için Word2Vec vektörünü hesaplar.
    Kelimelerin ortalama vektörünü döndürür.
    """
    word_vectors = []
    for word in words:
        if word in model.wv:  
            word_vectors.append(model.wv[word])
    
    if word_vectors: 
        return np.mean(word_vectors, axis=0)
    else:
        return None  

def query_analysis():
    while True:
        query = input("Aramak istediğiniz kelime veya kelimeleri girin (çıkmak için 'q'): ").strip()
        if query.lower() == 'q':
            print("Program sonlandırılıyor.")
            break

        query_tokens = [stemmer.stem(token) for token in word_tokenize(query.lower())]
        print(f"Temizlenmiş sorgu: {query_tokens}")

        query_vector = get_vector_for_multiple_words(model, query_tokens)

        if query_vector is not None:
            similar_words = model.wv.similar_by_vector(query_vector, topn=10)
            print(f"Eş anlamlı öneriler:")
            for word, score in similar_words:
                print(f"- {word} (Skor: {score:.4f})")
        else:
            print("Girilen kelimelerden hiçbiri modelde bulunamadı.")

if __name__ == "__main__":
    query_analysis()

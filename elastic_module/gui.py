import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
import threading

def run_flask():
    from flask import Flask, request, jsonify
    from elastic_search import search_articles
    from gensim.models import Word2Vec

    app = Flask(__name__)
    word_model = Word2Vec.load("w2v_custom_from_db.model")

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
            try:
                similar_words = word_model.wv.most_similar(query, topn=10)  
                synonyms = [word for word, _ in similar_words]
            except KeyError:
                synonyms = []
        return jsonify(synonyms)

    app.run(debug=True, use_reloader=False)  

def perform_search():
    search_input = entry.get()
    if search_input:
        elastic_response = requests.get(f"http://127.0.0.1:5000/search?query={search_input}")
        if elastic_response.status_code == 200:
            elastic_results = elastic_response.json()
            elastic_display = "\n\n".join([f"Title: {item['title']}\nURL: {item['url']}\nText: {item['text']}\n" for item in elastic_results])
        else:
            elastic_display = "Elasticsearch'te bir hata oluştu."

        word2vec_response = requests.get(f"http://127.0.0.1:5000/word2vec?query={search_input}")
        if word2vec_response.status_code == 200:
            synonyms = word2vec_response.json()
            word2vec_display = ", ".join(synonyms)
        else:
            word2vec_display = "Word2Vec'te bir hata oluştu."

        elastic_result_box.config(state=tk.NORMAL)
        elastic_result_box.delete(1.0, tk.END)
        elastic_result_box.insert(tk.END, elastic_display)
        elastic_result_box.config(state=tk.DISABLED)

        word2vec_result_box.config(state=tk.NORMAL)
        word2vec_result_box.delete(1.0, tk.END)
        word2vec_result_box.insert(tk.END, word2vec_display)
        word2vec_result_box.config(state=tk.DISABLED)
    else:
        messagebox.showwarning("Uyarı", "Lütfen bir kelime girin.")

def on_entry_click(event):
    if entry.get() == "Enter the word you want to search...":
        entry.delete(0, tk.END)  
        entry.config(fg="#d1d1d1")  

def on_focusout(event):
    if entry.get() == "":
        entry.insert(0, "Enter the word you want to search...") 
        entry.config(fg="#a6a6a6")  

root = tk.Tk()
root.title("Semantic Search")
root.geometry("900x600")
root.configure(bg="#121212")

title_label = tk.Label(root, text="Semantic Search", font=("Roboto", 24), bg="#121212", fg="#f1f1f1")
title_label.pack(pady=20)

frame = tk.Frame(root, bg="#121212")
frame.pack(pady=10)

entry = tk.Entry(frame, width=50, font=("Roboto", 12), bg="#2c2c2c", fg="#a6a6a6", borderwidth=0, highlightthickness=0)
entry.insert(0, "Enter the word you want to search...") 
entry.bind("<FocusIn>", on_entry_click)  
entry.bind("<FocusOut>", on_focusout)  
entry.pack(side=tk.LEFT, padx=10)

search_button = tk.Button(frame, text="Search", command=perform_search, font=("Roboto", 12), bg="#4caf50", fg="#ffffff", borderwidth=0)
search_button.pack(side=tk.LEFT)

result_frame = tk.Frame(root, bg="#121212")
result_frame.pack(pady=20)

word2vec_frame = tk.LabelFrame(result_frame, text="Word2Vec Synonyms", bg="#2c2c2c", fg="#f1f1f1", font=("Roboto", 12))
word2vec_frame.pack(side=tk.LEFT, padx=10, pady=10)

word2vec_result_box = scrolledtext.ScrolledText(word2vec_frame, width=40, height=20, bg="#2c2c2c", fg="#f1f1f1", state=tk.DISABLED)
word2vec_result_box.pack(padx=10)

elastic_frame = tk.LabelFrame(result_frame, text="Elasticsearch Results", bg="#2c2c2c", fg="#f1f1f1", font=("Roboto", 12))
elastic_frame.pack(side=tk.RIGHT, padx=10, pady=10)

elastic_result_box = scrolledtext.ScrolledText(elastic_frame, width=40, height=20, bg="#2c2c2c", fg="#f1f1f1", state=tk.DISABLED)
elastic_result_box.pack(padx=10)

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

root.mainloop()

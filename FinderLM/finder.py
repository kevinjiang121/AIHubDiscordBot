import json
import numpy as np
import tensorflow as tf
from tensorflow.python.keras.layers import Dense, Softmax
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertTokenizer, TFBertModel
import ijson
import sqlite3

json_file_path = r"Datasets\Posts.json"
sqlite_db_path = "posts.db"

def json_to_sqlite(file_path, db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS posts (content TEXT)")

    with open(file_path, "r", encoding="utf-8") as f:
        for post in ijson.items(f, "item"):
            try:
                c.execute("INSERT INTO posts (content) VALUES (?)", (post["content"],))
            except KeyError:
                continue

    conn.commit()
    conn.close()

json_to_sqlite(json_file_path, sqlite_db_path)

def read_posts_from_sqlite(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT content FROM posts")
    sentences = [row[0] for row in c.fetchall()]
    conn.close()
    return sentences

sentences_from_dataset = read_posts_from_sqlite(sqlite_db_path)

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
bert_model = TFBertModel.from_pretrained("bert-base-uncased")

def get_embeddings(sentences):
    embeddings = []
    for sentence in sentences:
        inputs = tokenizer(sentence, return_tensors="tf", truncation=True, padding=True, max_length=128)
        outputs = bert_model(inputs)
        embeddings.append(outputs.last_hidden_state[:, 0, :].numpy())
    return np.vstack(embeddings)

dataset_embeddings = get_embeddings(sentences_from_dataset)

class Attention(tf.keras.layers.Layer):
    def __init__(self, units):
        super(Attention, self).__init__()
        self.w = Dense(units, activation="tanh")
        self.softmax = Softmax(axis=1)

    def call(self, inputs):
        scores = self.w(inputs)
        weights = self.softmax(scores)
        attended_output = tf.reduce_sum(inputs * weights, axis=1)
        return attended_output

attention_layer = Attention(units=128)

def get_sentence_embedding_with_attention(sentence):
    inputs = tokenizer(sentence, return_tensors="tf", truncation=True, padding=True, max_length=128)
    outputs = bert_model(inputs)
    hidden_states = outputs.last_hidden_state
    attended_embedding = attention_layer(hidden_states)
    return attended_embedding.numpy()

input_sentence = "Son Goku"
input_embedding = get_sentence_embedding_with_attention(input_sentence)

similarities = [
    cosine_similarity(input_embedding, dataset_embedding.reshape(1, -1)).flatten()[0]
    for dataset_embedding in dataset_embeddings
]

most_related_index = np.argmax(similarities)
most_related_item = sentences_from_dataset[most_related_index]

print("Input Sentence:", input_sentence)
print("Most Related Item from Dataset:", most_related_item)

for i, sentence in enumerate(sentences_from_dataset):
    print(f"Similarity with dataset entry {i}: {similarities[i]:.4f}")

loss_function = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)

true_labels = tf.constant([0, 1, 2])
predicted_logits = tf.random.uniform((3, 5))
loss = loss_function(true_labels, predicted_logits)
print("Example Loss:", loss.numpy())

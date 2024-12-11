import numpy as np
import tensorflow as tf
from tensorflow.python.keras.layers import Dense, Softmax
from transformers import BertTokenizer, TFBertModel
from sklearn.metrics.pairwise import cosine_similarity

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
bert_model = TFBertModel.from_pretrained("bert-base-uncased")

def get_sentence_embedding_with_attention(sentence, attention_layer):
    inputs = tokenizer(sentence, return_tensors="tf", truncation=True, padding=True, max_length=128)
    outputs = bert_model(inputs)
    hidden_states = outputs.last_hidden_state
    attended_embedding = attention_layer(hidden_states)  
    return attended_embedding.numpy()

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
input_sentence = "Son Goku"
candidate_list = ["Dragonball", "Honkai", "Cartoon"]

input_embedding = get_sentence_embedding_with_attention(input_sentence, attention_layer)
candidate_embeddings = [
    get_sentence_embedding_with_attention(candidate, attention_layer) for candidate in candidate_list
]

similarities = [
    cosine_similarity(input_embedding, candidate_embedding).flatten()[0]
    for candidate_embedding in candidate_embeddings
]

most_related_index = np.argmax(similarities)
most_related_item = candidate_list[most_related_index]

print("Input Sentence:", input_sentence)
print("Most Related Item:", most_related_item)

for i, candidate in enumerate(candidate_list):
    print(f"Similarity with '{candidate}': {similarities[i]:.4f}")

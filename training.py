import json
import pickle
import random
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import SGD
from transformers import BertTokenizer, BertModel
import torch

# Load BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased')

# Load your utility functions or define them here
from utils import util  # Make sure utils/util.py is correctly defined

# Example intents data from your JSON
data_file = open('data.json').read()
intents = json.loads(data_file)

# Initialize lists for words, classes, and documents
words = []
classes = []
documents = []

# Process each intent and its patterns
for intent in intents['intents']:
    for pattern in intent['patterns']:
        # Preprocess the pattern
        pattern = pattern.lower()  # Convert to lowercase
        pattern = util.expand_contractions(pattern)  # Expand contractions
        w = tokenizer.tokenize(pattern)  # Tokenize using BERT tokenizer

        # Add to words list
        words.extend(w)

        # Add to documents
        documents.append((w, intent['tag']))

        # Add to classes if not already present
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

# Lemmatize words and remove duplicates
words = list(set(words))
words = sorted(words)

# Sort classes
classes = sorted(classes)

# Save words and classes to pickle files
pickle.dump(words, open('texts.pkl', 'wb'))
pickle.dump(classes, open('labels.pkl', 'wb'))

# Create training data
training = []

# Initialize empty array for output
output_empty = [0] * len(classes)

# Process each document to create bag of words
for doc in documents:
    bag = []
    pattern_words = doc[0]  # Tokenized words
    pattern_words = [word.lower() for word in pattern_words]  # Convert to lowercase

    # Generate BERT embeddings
    inputs = tokenizer(" ".join(pattern_words), return_tensors="pt")
    with torch.no_grad():
        outputs = bert_model(**inputs)

    # Get BERT embeddings
    embeddings = outputs.last_hidden_state.numpy()[0][0]  # Take the first token's embeddings

    # Create bag of words with BERT embeddings
    bag.append(embeddings)

    # Create output row - 0 for all classes except the current one
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1

    training.append([bag, output_row])

# Shuffle training data
random.shuffle(training)

# Convert training to numpy array
training = np.array(training, dtype=object)

# Separate features and labels
train_x = np.array([x[0][0] for x in training])
train_y = np.array([x[1] for x in training])

# Create Keras model
model = Sequential()
model.add(Dense(128, input_shape=(train_x.shape[1],), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(classes), activation='softmax'))

# Compile model
sgd = SGD(learning_rate=0.01, weight_decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

# Train model
history = model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)

# Save model
model.save('model_bert_integrated.h5')

print("BERT-integrated model created and saved.")

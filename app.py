import pickle
import numpy as np
import json
import random

from keras.models import load_model
from utils import util

# Load SDG model (assuming it's saved as 'sdg_model.h5')
model = load_model('model.h5')

# Load data and model files
intents = json.loads(open('data.json').read())
words = pickle.load(open('texts.pkl', 'rb'))
classes = pickle.load(open('labels.pkl', 'rb'))

def clean_up_sentence(sentence):
    # Lowercase all words 
    sentence = sentence.lower()

    # Remove contractions 
    sentence = util.expand_contractions(sentence)
    print('contractions', sentence)

    # Tokenize words
    sentence_words = util.tokenize_words(sentence)
    print('tokens', sentence_words)

    # Correct any sentence spelling mistake
    sentence_words = util.correct_spelling(sentence_words)
    print('correct', sentence_words)

    # Remove stop words 
    sentence_words = util.remove_stop_words(sentence_words)
    print('stop words', sentence_words)

    # Lemmatize and add similar words
    sentence_words = util.generate_variations(sentence_words)
    print('generate_variations', sentence_words)

    return sentence_words

def bow(sentence_words, words, show_details=True):
    # Bag of words - matrix of N words, vocabulary matrix
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                # Assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)

def predict_class(sentence, model):
    # 1. Tokenize ,
    # 2. Correct any spelling and grammar, 
    # 3. Lemmatize,
    sentence_clean = clean_up_sentence(sentence)
    print("sentence_clean", sentence_clean)

    # 4. Bag of words, once the msg is clean feed the bow with the sentence_clean
    bag_of_words = bow(sentence_clean, words, show_details=False)
    print("bag_of_words", bag_of_words)

    # 5. Convert to array 
    # 6. Feed the model 
    model_prediction_result = model.predict(np.array([bag_of_words]))[0]

    # Filter out predictions below a threshold
    ERROR_THRESHOLD = 0.25
    threshold_results = [[i, r] for i, r in enumerate(model_prediction_result) if r > ERROR_THRESHOLD]
    
    # 7. Return list of intents and probability related to the msg
    # Sort by strength of probability
    threshold_results.sort(key=lambda x: x[1], reverse=True)

    # Create an empty list to save results 
    return_list = []

    # Insert each result in the list 
    for r in threshold_results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})

    return return_list

def getResponse(ints, intents_json):
    # Extract the intent, that is related to a specific tag [{'intent': 'greeting', 'probability': '0.99934894'}]
    tag = ints[0]['intent']

    # Load data.json file into list_of_intents
    list_of_intents = intents_json['intents']

    # Search in the data.json for the specific tag and pick a random response
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

def updateJsonWithProbability(question, answer, probability):
    # Read JSON File
    with open('probability.json', 'r') as file:
        data = json.load(file)

    # Create model to save in json
    response = {
        "question": question,
        "response": answer,
        "probability": probability
    }

    # Add data to json
    data['responses'].append(response)

    # Write file
    with open('probability.json', 'w') as file:
        json.dump(data, file, indent=4)

def chatbot_response(msg):
    # Get the message, 
    # 1. Tokenize ,
    # 2. Correct any spelling and grammar, 
    # 3. Lemmatize,
    # 4. Bag of words, 
    # 5. Convert to array 
    # 6. Feed the model
    # 7. Save response in file 
    # 8. Return list of intents and probability related to the msg
    ints = predict_class(msg, model)
    print("intent related and probability --> ", ints)

    # Base on the intents (tags) result, pick first and get a random response
    res = getResponse(ints, intents)
    print("show response picked -->", res)

    # Save response 
    updateJsonWithProbability(msg, res, ints[0]['probability'])

    return res

from flask import Flask, render_template, request

app = Flask(__name__)
app.static_folder = 'static'

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["GET"])
def get_bot_response():
    userText = request.args.get('msg')
    if userText:
        try:
            response = chatbot_response(userText)
            return response
        except Exception as e:
            return f"An error occurred: {str(e)}", 500
    else:
        return "No message provided", 400

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=4900)

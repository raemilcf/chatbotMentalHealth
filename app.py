import pickle
import numpy as np
import json
import random



from keras.models import load_model
from utils import util


#load model
model = load_model('model.h5')

#load data and model files
intents = json.loads(open('data.json').read())
words = pickle.load(open('texts.pkl','rb'))
classes = pickle.load(open('labels.pkl','rb'))



def clean_up_sentence(sentence):

    #lower all words 
    sentence = sentence.lower()

    #remove contractions 
    sentence = util.expand_contractions(sentence)
    print('contractions',sentence)

    #tokenize words
    sentence_words =util.tokenize_wrods(sentence)
    print('tokens',sentence_words)

    #correct any sentence spelling mistake
    sentence_words = util.correct_spelling(sentence_words)
    print('correct',sentence_words)

    #remove stop words 
    sentence_words = util.remove_stop_words(sentence_words)
    print('stop words',sentence_words)

    # lemmatize and add similar words
    sentence_words = util.generate_variations(sentence_words)
    print('generate_variations',sentence_words)

    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence_words, words, show_details=True):
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):

    # 1. tokenize ,
    # 2. correct any spelling and grammar, 
    # 3. lemmatize,
    sentence_clean = clean_up_sentence(sentence)
    print("sentence_clean",sentence_clean)

    # 4.bag of words, once the msg is clean feed the bow with the sentence_clean
    bag_of_words = bow(sentence_clean, words,show_details=False)
    print("bag_of_words",bag_of_words)

    # 5. convert to array 
    # 6. feed the model 
    model_prediction_result = model.predict(np.array([bag_of_words]))[0]

    # filter out predictions below a threshold
    ERROR_THRESHOLD = 0.25
    threshold_results = [[i,r] for i,r in enumerate(model_prediction_result) if r>ERROR_THRESHOLD]
    
    # 7. return list of intents and probability related to the msg
    # sort by strength of probability
    threshold_results.sort(key=lambda x: x[1], reverse=True)

    #create a empty list to save results 
    return_list = []

    #insert each result in the list 
    for r in threshold_results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})

    return return_list

def getResponse(ints, intents_json):
    #extrat the intent, that is related to a specific tag [{'intent': 'greeting', 'probability': '0.99934894'}]
    tag = ints[0]['intent']

    #load data.json file into list_of_intents
    list_of_intents = intents_json['intents']

    #search in the data.json for the specific tag and pick a random response
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

def updateJsonWithProbability(question, answer, probability):
    # read Json File
    with open('probabiltiy.json', 'r') as file:
        data = json.load(file)

    # create model to save in json
    response = {
        "question": question,
        "response": answer,
        "probability": probability
    }

    #add data to json
    data['responses'].append(response)

    # write file
    with open('probabiltiy.json', 'w') as file:
        json.dump(data, file, indent=4)


def chatbot_response(msg):
    #get the message, 
    # 1. tokenize ,
    # 2. correct any spelling and grammar, 
    # 3. lemmatize,
    # 4.bag of words, 
    # 5. convert to array 
    # 6. feed the model
    # 7. save response in file 
    # 8. return list of intents and probability related to the msg
    ints = predict_class(msg, model)
    print("intent related and probability --> ",ints)

    #base on the intents (tags) result, pick first and get a random response
    res = getResponse(ints, intents)
    print("show response picked -->",res)

    #save response 
    # updateJsonWithProbability(msg,res, ints[0]['probability'])

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
    app.run()
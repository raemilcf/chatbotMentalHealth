import nltk
import re
import inflect
import string


from nltk.corpus import stopwords
from nltk.corpus import wordnet
from itertools import product
from nltk.stem import WordNetLemmatizer
from autocorrect import Speller

#download stop words
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('popular')

#create instance of lemma
lemmatizer = WordNetLemmatizer()

#create instance of spell correction 
spell = Speller(lang='en')

#initialize engine
inflect_engine = inflect.engine()


#list of possible contractions to fix any grammar and provide best answer
contractions_dict = {
    "ain't": "am not",
    "aren't": "are not",
    "can't": "cannot",
    "can't've": "cannot have",
    "'cause": "because",
    "could've": "could have",
    "couldn't": "could not",
    "couldn't've": "could not have",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hadn't've": "had not have",
    "hasn't": "has not",
    "haven't": "have not",
    "he'd": "he would",
    "he'd've": "he would have",
    "he'll": "he will",
    "he'll've": "he will have",
    "he's": "he is",
    "how'd": "how did",
    "how'd'y": "how do you",
    "how'll": "how will",
    "how's": "how is",
    "i'd": "i would",
    "i'd've": "i would have",
    "i'll": "i will",
    "i'll've": "i will have",
    "i'm": "i am",
    "i've": "i have",
    "isn't": "is not",
    "it'd": "it would",
    "it'd've": "it would have",
    "it'll": "it will",
    "it'll've": "it will have",
    "it's": "it is",
    "let's": "let us",
    "ma'am": "madam",
    "mayn't": "may not",
    "might've": "might have",
    "mightn't": "might not",
    "mightn't've": "might not have",
    "must've": "must have",
    "mustn't": "must not",
    "mustn't've": "must not have",
    "needn't": "need not",
    "needn't've": "need not have",
    "o'clock": "of the clock",
    "oughtn't": "ought not",
    "oughtn't've": "ought not have",
    "shan't": "shall not",
    "sha'n't": "shall not",
    "shan't've": "shall not have",
    "she'd": "she would",
    "she'd've": "she would have",
    "she'll": "she will",
    "she'll've": "she will have",
    "she's": "she is",
    "should've": "should have",
    "shouldn't": "should not",
    "shouldn't've": "should not have",
    "so've": "so have",
    "so's": "so is",
    "that'd": "that would",
    "that'd've": "that would have",
    "that's": "that is",
    "there'd": "there would",
    "there'd've": "there would have",
    "there's": "there is",
    "they'd": "they would",
    "they'd've": "they would have",
    "they'll": "they will",
    "they'll've": "they will have",
    "they're": "they are",
    "they've": "they have",
    "to've": "to have",
    "wasn't": "was not",
    "we'd": "we would",
    "we'd've": "we would have",
    "we'll": "we will",
    "we'll've": "we will have",
    "we're": "we are",
    "we've": "we have",
    "weren't": "were not",
    "what'll": "what will",
    "what'll've": "what will have",
    "what're": "what are",
    "what's": "what is",
    "what've": "what have",
    "when's": "when is",
    "when've": "when have",
    "where'd": "where did",
    "where's": "where is",
    "where've": "where have",
    "who'll": "who will",
    "who'll've": "who will have",
    "who's": "who is",
    "who've": "who have",
    "why's": "why is",
    "why've": "why have",
    "will've": "will have",
    "won't": "will not",
    "won't've": "will not have",
    "would've": "would have",
    "wouldn't": "would not",
    "wouldn't've": "would not have",
    "y'all": "you all",
    "y'all'd": "you all would",
    "y'all'd've": "you all would have",
    "y'all're": "you all are",
    "y'all've": "you all have",
    "you'd": "you would",
    "you'd've": "you would have",
    "you'll": "you will",
    "you'll've": "you will have",
    "you're": "you are",
    "you've": "you have"
}

#create contraction list separate by pipe
contractions_re = re.compile('(%s)' % '|'.join(contractions_dict.keys()))

# Add all punctuation characters
ignore_words=[]
ignore_words.extend(string.punctuation)
# Remove duplicates by converting to a set and back to a list
ignore_words = list(set(ignore_words))

#tokenize words
def tokenize_wrods(sentence):
     # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)

    return sentence_words

#correct spelling 
def correct_spelling(words_list):

    #correct each word, iterate and use the autocorrect to return appropiate word
    corrected_list = [spell(word) for word in words_list]

    return corrected_list


#correct contractions to original form ex I'm -> I am
def expand_contractions(sentence, contractions_dict=contractions_dict):
    def replace(match):
        #find  if any contraction exist 
        return contractions_dict[match.group(0)]
    #remove replace contraction for original form
    return contractions_re.sub(replace, sentence)

#remove stop words 
def remove_stop_words(words_list):
    #get the English stopwords
    stop_words = set(stopwords.words('english'))

    # Remove stopwords iterate if word is not in the stopword then I added to list
    corrected_list = [word for word in words_list if word not in stop_words]
    corrected_list = [word for word in words_list if word not in ignore_words]

    return corrected_list

#get word tags noun,verb,adverb, adjetive 
def get_wordnet_pos(word):
    
    #identify the tag that correspond
    tag = nltk.pos_tag([word])[0][1][0].upper()
   
    #create a tag dict
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    
    #return type of word noun,verb,adverb, adjetive 
    return tag_dict.get(tag, wordnet.NOUN)

def generate_variations(sentence_words):
    
    all_variations=[]
    for word in sentence_words:
        #lemma word by type 
        lemmatized_word = lemmatizer.lemmatize(word, get_wordnet_pos(word))
        #add to a variations, example if the sentences is I'm starving 
        #will be added [starve,starving]
        word_variations = set([word, lemmatized_word] )
        
        # Add singular and plural forms if the word is a noun, if is a noun
        #to increase our matching chances ex. people, person etc
        if get_wordnet_pos(word) == wordnet.NOUN:
            #add singular and plural of origninal word
            word_variations.add(inflect_engine.singular_noun(word) or word)
            word_variations.add(inflect_engine.plural_noun(word) or word)
            #add s and p of lemma 
            word_variations.add(inflect_engine.singular_noun(lemmatized_word) or lemmatized_word)
            word_variations.add(inflect_engine.plural_noun(lemmatized_word) or lemmatized_word)
        
        #for initial stage we will add everything to the senctence
        #like it was part of it ex. [starve, starving]
        for variation in word_variations:
            all_variations.append(variation)

    #return all the sentence_word + variations 
    return all_variations

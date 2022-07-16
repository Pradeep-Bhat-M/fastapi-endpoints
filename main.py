from fastapi import FastAPI, Depends
import pickle, re
# from numpy.lib.function_base import vectorize
# from sklearn.feature_extraction.text import CountVectorizer
# import pandas as pd


app = FastAPI()

blocks = []
languages_dict = {}


def load_preprocessing():
    # Get file by name
    # Open file and load model
    object_path = "count_vectorizer.pkl"
    #object_path = client.file(file_path).getFile().name
    # Open file and preprocessin object
    with open(object_path, 'rb') as f:
        object = pickle.load(f)
        return object    

def load_model():
    model_path = "langIdentify.pkl"
    #model_path = client.file(file_path).getFile().name
    # Open file and load model
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
        return model

def parseInput(textIn):
    data = re.sub(' +', ' ', textIn)                  # Removing redundant multiple spaces
    data = re.sub('\n+',' ', data)                    # Removing extra lines
    data = re.sub('/+','',data)
    data = re.sub(',+','',data)
    data = re.sub('\.+','',data)
    data = re.sub('_', ' ', data)

    return data.split(' ')

def addInDictionary(language, word):                  # Adding words into a dictionary
    if language in languages_dict:
        languages_dict.get(language).append(word)
    else:
        languages_dict[language] = [word]

def block(unicode):                                   # Comparing Unicode ranges to find the script
    for start, end, name in blocks:
        if start <= unicode <= end:
            return start, end, name
    return 0, 0, "No Such Script Can be Identified"

def makeBlocks(code_file):                            # Loading all the Unicode ranges

    file = open(code_file)
    text = file.read()

    pattern = re.compile(r'([0-9A-F]+)\.\.([0-9A-F]+);\ (\S.*\S)')
    for line in text.splitlines():
        m = pattern.match(line)
        if m:
            start, end, name = m.groups()
            blocks.append((int(start, 16), int(end, 16), name))  # Converting hexString to Integer
# Load model outside of the apply function so it only gets loaded once

makeBlocks("unicodes.txt")
# model = load_model()
# vectorizer = load_preprocessing()

@app.get('/')
async def root():
    return {'message': 'Hello World!'}

@app.post('/{text}')
def predictLang(text: str):

    prevLang = (65, 122, 'English')
    #text = text.split('_')
    #print(text)
    dataByWOrds = parseInput(text)
    for word in dataByWOrds:
        # word = re.sub('\W+', '', word)  # Removing Special Character
        # word = re.sub('[0-9]+', '', word)  # Removing Numbers
        if not word:
            continue
        unicode = ord(word[0])  # Fetching the unicode of the character
        if prevLang[0] <= unicode <= prevLang[1]:
            language = prevLang[2]
        else:
            prevLang = block(unicode)  # Updating prevLang, so that we need not search the whole unicode block again.
            language = prevLang[2]
        addInDictionary(language, word)

    #if(languages_dict[0].find("Latin")[0] == -1):
    lang = list(languages_dict.keys())
    languages_dict.clear()    
    return lang
    # vectorizer = load_preprocessing()
    # find = vectorizer.transform([text])
    # test_find = pd.DataFrame(find.toarray())

    # #with open("langIdentify.pkl", "rb") as rfcModel:
    # model = load_model()
    # return model.predict([test_find])
    # return ["Can't predict"]
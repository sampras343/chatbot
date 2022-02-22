
import json
import nltk

words = []
labels = []
docs_x = []
docs_y = []

with open("trainingData.json") as file:
    data = json.load(file)

for intent in data["intents"]:
    for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])
            if intent["tag"] not in labels:
                labels.append(intent["tag"])


print("Words :: ", words)
print("Labels :: ", labels)
print("Docs X :: ", docs_x)
print("Docs Y :: ", docs_y)


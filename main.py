import paho.mqtt.client as publish
from nltk.stem.lancaster import LancasterStemmer
from datetime import datetime
import tflearn
import tensorflow
import numpy
import json
import random
import pickle
import nltk
import threading
import client
import os
import requests
import json
from var import nodeinfo
from selenium import webdriver
import time

# print "Socket successfully created"
broker = "localhost"
port = 1883


try:
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)
except:
    words = []  # individual words
    labels = []  # tags
    docs_x = []  # contents inside pattern
    docs_y = []  # corresponding tag of a specific pattern mapped with index


def on_publish(client, userdata, result):  # create function for callback
    pass


client1 = publish.Client("control1")

model = None
stemmer = LancasterStemmer()
data = None
allNodesInPortal = []


def train(retrain):
    global model, words, labels, docs_x, docs_y, stemmer, data
    # nltk.download('punkt')
    # from client import transferData

    with open("training_data.json") as file:
        data = json.load(file)
    try:
        with open("data.pickle", "rb") as f:
            words, labels, training, output = pickle.load(f)
    except:
        words = []  # individual words
        labels = []  # tags
        docs_x = []  # contents inside pattern
        docs_y = []  # corresponding tag of a specific pattern mapped with index
        for intent in data["intents"]:
            for pattern in intent["patterns"]:
                wrds = nltk.word_tokenize(pattern)
                words.extend(wrds)
                docs_x.append(wrds)
                docs_y.append(intent["tag"])
                if intent["tag"] not in labels:
                    labels.append(intent["tag"])

        # Stem all the words to remove duplicates
        words = [stemmer.stem(w.lower()) for w in words if w != "?"]

        # Make a set out of the words list in order to remove the duplicates and convert it back to set
        words = sorted(list(set(words)))
        labels = sorted(labels)

        # Right now we have strings. Neural network understands only numbers. So create a bag of words that represents all of the words in any given pattern to train the model

        training = []
        output = []

        out_empty = [0 for _ in range(len(labels))]

        for x, doc in enumerate(docs_x):
            bag = []

            wrds = [stemmer.stem(w.lower()) for w in doc]
            for w in words:
                if w in wrds:
                    bag.append(1)
                else:
                    bag.append(0)
            output_row = out_empty[:]
            output_row[labels.index(docs_y[x])] = 1

            training.append(bag)
            output.append(output_row)

        training = numpy.array(training)
        output = numpy.array(output)

        with open("data.pickle", "wb") as f:
            pickle.dump((words, labels, training, output), f)

    tensorflow.reset_default_graph()

    net = tflearn.input_data(shape=[None, len(training[0])])
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
    net = tflearn.regression(net)

    model = tflearn.DNN(net)

    try:
        if retrain == "true":
            model.fit(training, output, n_epoch=500,
                      batch_size=16, show_metric=True)
            model.save("model.tflearn")
            model.load("model.tflearn")
        else:
            model.load("model.tflearn")
    except:
        model.fit(training, output, n_epoch=500,
                  batch_size=16, show_metric=True)
        model.save("model.tflearn")


def bag_of_words(s, words):
    global model, labels, docs_x, docs_y, stemmer, data
    bag = [0 for _ in range(len(words))]
    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
    return numpy.array(bag)


def chat(msg):
    global model, words, labels, docs_x, docs_y, data, allNodesInPortal, nodes
    allNodesInPortal = []
    train('false')
    focusIOElement = ''
    with open("schema.json") as f:
        schema = json.load(f)
    results = model.predict([bag_of_words(msg, words)])[0]
    results_index = numpy.argmax(results)
    tag = labels[results_index]
    if results[results_index] > 0.7:
        if tag == "time":
            for tg in data["intents"]:
                if tg['tag'] == "time":
                    responses = tg['responses']
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    break
            print(random.choice(responses), current_time)
            client1.on_publish = on_publish
            client1.connect(broker, port)
            client1.publish("test", random.choice(responses)+" "+current_time)
        elif tag == "updatechatbot":
            os.remove("model.tflearn.index")
            os.remove("model.tflearn.data-00000-of-00001")
            os.remove("model.tflearn.meta")
            os.remove("data.pickle")
            os.remove("checkpoint")
            client1.on_publish = on_publish
            client1.connect(broker, port)
            client1.publish("test", "Give me a moment... Keeping myself up to date")
            train("true")
        else:
            rootIdentifier = tag.split('_')
            print(rootIdentifier)
            #print('Schema', schema['screens'])
            if rootIdentifier[0] == "screen":
                for scr in schema['screens']:
                    print("In Loop", tag)
                    index = schema['screens'].index(scr)
                    length = len(schema['screens'])
                    if scr['tag'] == tag:
                        responseToDisplay = "Switching to "+ str(scr['nameToDisplay'])
                        responseToFrontend = scr['screenName'] 
                        print('responseToDisplay', responseToDisplay)
                        print('responseToFrontend', responseToFrontend)
                        client1.on_publish = on_publish
                        client1.connect(broker, port)
                        client1.publish("test", responseToDisplay)
                        client1.publish("screenswitch", responseToFrontend)
                        break
                    elif index == length - 1 and scr['tag'] != tag:
                        responseToDisplay = "No Such Screen"
                        print('responseToDisplay', responseToDisplay)
                        client1.on_publish = on_publish
                        client1.connect(broker, port)
                        client1.publish("test", responseToDisplay)
            elif rootIdentifier[0] == "button":
                for btn in schema['buttons']:
                    index = schema['buttons'].index(btn)
                    length = len(schema['buttons'])
                    if btn['tag'] == tag:
                        responseToDisplay = "Engaging "+ str(btn['nameToDisplay'])
                        buttonName = btn['buttonName']
                        responseToFrontEnd = {
                            "name" : buttonName,
                            "action" : "Down"
                        }
                        responseToJson = json.dumps(responseToFrontEnd)
                        print(responseToJson)
                        client1.on_publish = on_publish
                        client1.connect(broker, port)
                        client1.publish("test", responseToDisplay)
                        client1.publish("fireevent", responseToJson)
                        break
            elif rootIdentifier[0] == "check":
                print("IN If",rootIdentifier)
                for chk in schema['checkboxes']:
                    print("IN Loop",chk)
                    print("IN Loop tag",tag)
                    index = schema['checkboxes'].index(chk)
                    length = len(schema['checkboxes'])
                    if chk['tagPositive'] == tag:
                        responseToDisplay = "Selecting "+ str(chk['nameToDisplay'])
                        checkBoxName = chk['checkBoxName']
                        responseToFrontEnd = {
                            "path" : checkBoxName,
                            "value" : True,
                            "name":"ProcessValue"
                        }
                        responseToJson = json.dumps(responseToFrontEnd)
                        print(responseToJson)
                        client1.on_publish = on_publish
                        client1.connect(broker, port)
                        client1.publish("test", responseToDisplay)
                        client1.publish("setiovalue", responseToJson)
                        break
                    elif chk['tagNegative'] == tag:
                        responseToDisplay = "Deselecting "+ str(chk['nameToDisplay'])
                        checkBoxName = chk['checkBoxName']
                        responseToFrontEnd = {
                            "path" : checkBoxName,
                            "value" : False,
                            "name":'ProcessValue'
                        }
                        responseToJson = json.dumps(responseToFrontEnd)
                        print(responseToJson)
                        client1.on_publish = on_publish
                        client1.connect(broker, port)
                        client1.publish("test", responseToDisplay)
                        client1.publish("setiovalue", responseToJson)
                        break
            elif rootIdentifier[0] == "iofocus":
                for iof in schema['iofields']:
                    index = schema['iofields'].index(iof)
                    length = len(schema['iofields'])
                    if io['focusTag'] == tag:
                        focusIOElement = iof['ioFieldName']
                        responseToDisplay = "Focus is on " + str(iof['ioFieldName']) + ". Provide a value to be set"
                        client1.on_publish = on_publish
                        client1.connect(broker, port)
                        client1.publish("test", responseToDisplay)
                        break
            elif rootIdentifier[0] == "ioset":
                for io in schema['iofields']:
                    index = schema['iofields'].index(io)
                    length = len(schema['iofields'])
                    if io['tag'] == tag:
                        
                        responseToDisplay = ""
                        client1.on_publish = on_publish
                        client1.connect(broker, port)
                        client1.publish("test", responseToDisplay)
                        focusIOElement = ''
                        break
            else:
                for tg in data["intents"]:
                    if tg['tag'] == tag:
                        responses = tg['responses']
                print(random.choice(responses))
                client1.on_publish = on_publish
                client1.connect(broker, port)
                client1.publish("test", random.choice(responses))
                    

        # else:
        #     for tg in data["intents"]:
        #         if tg['tag'] == tag:
        #             responses = tg['responses']
        #     print(random.choice(responses))
        #     client1.on_publish = on_publish
        #     client1.connect(broker, port)
        #     client1.publish("test", random.choice(responses))
    else:
        print("I didn't get that, try again")
        client1.on_publish = on_publish
        client1.connect(broker, port)
        client1.publish("test", "I didn't get that, try again")


if __name__ == "__main__":
    c = client.sub()
    t = threading.Thread(target=c.connect())
    t.start()

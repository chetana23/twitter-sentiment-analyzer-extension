# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_app]
# [START gae_python3_app]
from flask import Flask, request
from langdetect import detect
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
from flask_cors import CORS, cross_origin

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return 'Hello World!'

# load model and tokenizer
roberta = "cardiffnlp/twitter-roberta-base-sentiment"
model = AutoModelForSequenceClassification.from_pretrained(roberta)
tokenizer = AutoTokenizer.from_pretrained(roberta)

labels = ['Negative', 'Neutral', 'Positive']

# pre-process tweet and get rid of any @mention and url http
def process(tweet:str):
    tweet_words = []
    for word in tweet.split(' '):
        if word.startswith('@') and len(word) > 1:
            word = '@user'
        
        elif word.startswith('http'):
            word = "http"
        tweet_words.append(word)

    tweet_proc = " ".join(tweet_words)
    encoded_tweet = tokenizer(tweet_proc, return_tensors='pt')
    return encoded_tweet


#language detecting API
@app.route('/api/language-detection', methods = ['POST'])
def detectLanguage():
    res = []
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        data = request.json
        for i in data:
            map = {}
            detect(i['tweet_text'])
            map['tweet_text'] = i['tweet_text']
            map['is_english'] = True if detect(i['tweet_text']) == 'en' else False
            res.append(map)
        return res
    else:
        return "Content type is not supported."

#sentiment analysing API
@app.route('/api/sentiment-score', methods = ['POST'])
def detectSentiment3():
    res = []
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        data = request.json
        for i in data:
            encoded_tweet = process(i['tweet_text'])
            output = model(**encoded_tweet)
            scores = output[0][0].detach().numpy()
            scores = softmax(scores)
            senti = {}
            mapVal = {}
            maxVal = 0
            for val in range(len(scores)):
                if scores[val] > maxVal:
                    maxVal = scores[val]
                    mapVal['detected_mood'] = labels[val].upper() 
                senti[labels[val]] = str(scores[val])
            mapVal["sentiment_score"] = senti
            mapVal['tweet_text'] = i['tweet_text']
            res.append(mapVal)
        return res
    else:
        return "Content type is not supported."

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. You
    # can configure startup instructions by adding `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python3_app]
# [END gae_python38_app]

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
from flask_cors import CORS, cross_origin
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
CORS(app)

sentiment = SentimentIntensityAnalyzer()


@app.route('/')
def hello():
    return 'Hello World!'

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

#sentiment analysis
@app.route('/api/sentiment-score', methods = ['POST'])
def detectSentiment2():
    res = []
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        data = request.json
        for i in data:
            mapVal = {}
            senti = {}
            val = sentiment.polarity_scores(i['tweet_text'])
            print(val)
            mood = val['compound']
            if mood >= 0.05:
                mapVal['detected_mood'] = "POSITIVE"
            elif mood <= -0.05:
                mapVal['detected_mood'] = "NEGATIVE"
            else:
                mapVal['detected_mood'] = "NEUTRAL"
            senti["positive"] = val['pos']
            senti["negative"] = val['neg']
            senti["neutral"] = val['neu']
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

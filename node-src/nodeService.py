from flask import Flask, request
from gpt import Prompt
from log import log
from gevent import pywsgi
from sys import argv
import requests
import json
import os

app = Flask(__name__)

url = "https://api.openai.com/v1/completions"  # openai API prefix
API_KEY = ''  # API key
prompt = Prompt()  # single entity mode
max_retry = 3  # max retry times


def environCheck() -> None:
    global API_KEY
    try:
        API_KEY = os.environ['BEARER_TOKEN']
    except KeyError:
        API_KEY = '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'


def requestGPT(prompt: str) -> (str, Exception):
    payload = json.dumps({
        "model": "text-davinci-003",
        "prompt": prompt,
        "max_tokens": 2048
    })
    headers = {
        'Authorization': 'Bearer ' + API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload, verify=False, timeout=(1.0, 6.0))

    try:
        log.info('Success on request openai')
        log.info(prompt)
        log.info(response.json())
        return str(response.json()['choices'][0]['text']), None
    except Exception as e:
        log.error(e)
        return 'Failed to request GPT.\n{}'.format(e), e


@app.route('/')
def hello():
    return "Hello world."


@app.route('/emotion', methods=['GET'])
def emotion():
    # unpack request
    emotion = request.args.get('mood')  # missing validation, more safety to add a validated

    if emotion is None:
        log.warning('/emotion doesn\'t receive any params.')
        return 'Oops, wrong request params'

    log.info('/emotion Param keys: ' + str(request.args.keys()))
    log.info('/emotion Recv params: ' + emotion)

    for i in range(max_retry):  # retry mechanism
        result, error = requestGPT(prompt.emotion(emotion))

        if error is not None:
            return 'Oops, server is very busy right now, maybe you can access again later?'

        if result is not None and result != '':
            return result


@app.route('/review', methods=['GET'])  # generate random comment for a movie
def comment():
    movie_name = request.args.get('movie')

    if movie_name is None:
        log.warning('/review doesn\'t receive any params.')
        return 'Oops, wrong request params'

    log.info('/review Param keys: ' + str(request.args.keys()))
    log.info('/review Recv params: ' + movie_name)

    log.info('/comment request recv, Movie: ' + movie_name)  # log module
    result, error = requestGPT(prompt.comment(movie_name))

    if error is not None:
        return 'Oops, server have some little problem, can you retry it a bit later?'

    return result


@app.route('/recommend', methods=['GET'])
def recommend():
    mood = request.args.get('mood')

    if mood is None:
        log.info('/recommend Request may have no params')

    log.info('/recommend Param keys: ' + str(request.args.keys()))
    log.info('/recommend Recv params: ' + mood)

    result, error = requestGPT(prompt.recommend(mood))

    if error is not None:
        return 'Oops, server have some little problem, can you retry it a bit later?'

    log.info('/recommend request recv, Movie: ' + result)
    return result


if __name__ == '__main__':
    environCheck()

    print(argv)

    if argv[1] == 'dev':
        # dev mode
        app.run(host='0.0.0.0', port=4000)
    elif argv[1] == 'help':
        print("Only one param accepted:"
              "dev: development mode."
              "help: show this help prompt."
              "DEFAULT = production mode")
    else:
        # production mode
        server = pywsgi.WSGIServer(('0.0.0.0', 4000), app)
        server.serve_forever()

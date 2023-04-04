from flask import Flask, request, abort
from gpt import Prompt
from log import log
import requests
import json

app = Flask(__name__)

url = "https://api.openai.com/v1/completions"  # openai API
prompt = Prompt()  # single entity mode
max_retry = 3


def requestGPT(prompt: str) -> (str, Exception):
    payload = json.dumps({
        "model": "text-davinci-003",
        "prompt": prompt,
        "max_tokens": 2048
    })
    headers = {
        'Authorization': 'Bearer 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',
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
    try:
        # unpack request
        emotion = request.args.get('mood')  # missing validation, more safety to add a validated
        log.info('/emotion Param keys: ' + str(request.args.keys()))
    except Exception as e:
        log.error('/emotion error \n Err: ' + str(e))
        log.warning('/emotion doesn\'t receive any params.')
        return 'Oops, wrong request params'

    for i in range(max_retry):  # retry mechanism
        result, error = requestGPT(prompt.emotion(emotion))

        if error is not None:
            return 'Oops, server is very busy right now, maybe you can access again later?'

        if result is not None and result != '':
            return result


@app.route('/review', methods=['GET'])  # generate random comment for a movie
def comment():
    try:
        # unpack request
        movie_name = request.args.get('movie')
        log.info('/review Param keys: ' + str(request.args.keys()))
    except Exception as e:
        log.error('/review error \n Err: ' + str(e))
        log.warning('/review doesn\'t receive any params.')
        return 'Oops, wrong request params'

    log.info('/comment request recv, Movie: ' + movie_name)  # log module
    result, error = requestGPT(prompt.recommend(movie_name))

    if error is not None:
        return 'Oops, server have some little problem, can you retry it a bit later?'

    return result


@app.route('/recommend', methods=['GET'])
def recommend():
    try:
        mood = request.args.get('mood')
        log.info('/recommend Param keys: ' + str(request.args.keys()))
    except RuntimeError as e:
        log.error(e)
        log.info('/recommend Request may have no params')
        mood = None

    result, error = requestGPT(prompt.recommend(mood))

    if error is not None:
        return 'Oops, server have some little problem, can you retry it a bit later?'

    log.info('/recommend request recv, Movie: ' + result)
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)

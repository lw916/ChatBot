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
    response = requests.request("POST", url, headers=headers, data=payload)

    try:
        log.info('Success on request openai')
        log.info(prompt)
        return str(response.json()['choices'][0]['text']), None
    except Exception as e:
        log.error(e)
        return 'Failed to request GPT.\n{}'.format(e), e


@app.route('/')
def hello():
    return "Hello world."


@app.route('/down')
def down():
    for i in range(max_retry):
        result, error = requestGPT(prompt.down_prompt)

        if result is not None and result != '':
            return result

        if error is not None:
            return 'Oops, server is very busy right now, maybe you can access again later?'


@app.route('/review', methods=['GET'])  # generate random comment for a movie
def comment():
    try:
        # unpack request
        movie_name = request.args.get('movie')
    except Exception as e:
        log.error('/comment error \n Err: ' + str(e))
        log.warning('/comment doesn\'t receive any params.')
        return 'Oops, wrong request params'

    log.info('/comment request recv, Movie: ' + movie_name)  # log module
    result, error = requestGPT(prompt.down_prompt)

    if error is not None:
        return 'Oops, server have some little problem, can you retry it a bit later?'

    return result


@app.route('/recommend', methods=['GET'])
def recommend():
    try:
        mood = request.args.get('mood')
        log.info('Param keys: ' + str(request.args.keys()))
    except RuntimeError as e:
        log.error(e)
        log.info('Request may have no params')
        log.info('Param keys: ' + str(request.args.keys()))
        mood = None

    if mood == '' or mood is None:
        result, error = requestGPT(prompt.recommend_prompt)
    else:
        result, error = requestGPT(prompt.recommend_prompt(mood))

    if error is not None:
        return 'Oops, server have some little problem, can you retry it a bit later?'

    log.info('/recommend request recv, Movie: ' + result)
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)

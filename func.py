from flask import make_response


def handle_challenge(challenge):
    response = make_response(challenge, 200)
    response.headers["Content-type"] = "application/json"
    return response


def response_error():
    response = make_response(
        "There are no slack request events", 404, {"X-Slack-No-Retry": 1}
    )
    return response


def response_ok():
    response = make_response("OK", 200)
    return response

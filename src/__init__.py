from flask import Flask, request
from src.config import Config

config = Config("config.json")

app = Flask("MailServer")


@app.route("/mail/send/", methods=["POST"])
def send():
    requirements = ["receiver", "subject", "body"]
    for requirement in requirements:
        if requirement not in request.data:
            return {"success": False, "status": 400, "message": f"Missing requirement {requirement}"}, 400
    return {"success": True, "status": 200, "message": "Message send."}, 200


@app.errorhandler(404)
def not_found(error):
    app.logger.info(f"404 error -> {request.path} by {request.remote_addr}")
    return {"success": False, "status": 404, "message": "Page not found."}, 404

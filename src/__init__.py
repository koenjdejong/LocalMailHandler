from flask import Flask, request
from src.config import Config

config = Config("config.json")
app = Flask("MailServer")

from src.mail import MailService

with app.app_context():
    # TODO Still executes this twice.
    mail_service = MailService()
    # mail_service.send_message("k.j.dejong@student.utwente.nl", "Server started.",
    #                           '''Dear Koen de Jong,
    #
    # I would hereby like to inform you that the MailServer has been started.
    #
    # Kind regards,
    #
    # Koen de Jong''')
    app.logger.info("MailServer started and startup mail sent.")


@app.route("/mail/send/", methods=["POST"])
def mail_send():
    # Verify of data exists
    if request.form:
        app.logger.error(
            f"400 error -> {request.path} by {request.remote_addr}, form data is not allowed: {request.form}")
        return {"success": False, "status": 400, "message": "Form data is not accepted."}, 400
    if not request.data:
        app.logger.error(f"400 error -> {request.path} by {request.remote_addr}, no data provided")
        return {"success": False, "status": 400, "message": "No data could be found"}, 400

    # Checking if all data is present
    data = request.json
    requirements = ["receiver", "subject", "body"]
    for requirement in requirements:
        if requirement not in data:
            app.logger.error(f"400 error -> {request.path} by {request.remote_addr}, missing {requirement}")
            return {"success": False, "status": 400, "message": f"Missing requirement {requirement}"}, 400

    # TODO: send email

    app.logger.info(
        f"200 status -> {request.path} by {request.remote_addr}, sending email to '{data['receiver']}' with subject '{data['subject']}' and body '{data['body']}'")

    return {"success": True, "status": 200, "message": "Message send."}, 200


@app.route("/mail/test/", methods=["POST"])
def mail_test():
    app.logger.info(
        f"200 status -> {request.path} by {request.remote_addr}, sending test email to '{config['mail']['recipient_email']}'")
    mail_service.send_email(config['mail']['recipient_email'], "Test email", "This is a test email.")
    return {"success": True, "status": 200, "message": "Test message sent."}, 200


@app.route("/form/submit/", methods=["POST"])
def submit():
    return {"success": False, "status": 500, "message": "Not implemented yet."}, 500


@app.errorhandler(405)
def not_found(error):
    app.logger.error(f"405 error -> {request.method} to {request.path} by {request.remote_addr}")
    return {"success": False, "status": 405, "message": f"Method {request.method} not allowed"}, 405


@app.errorhandler(404)
def not_found(error):
    app.logger.error(f"404 error -> {request.path} by {request.remote_addr}")
    return {"success": False, "status": 404, "message": "Page not found."}, 404

from flask import Flask, request, render_template
from src.config import Config


config = Config("config.json")
from honeybadger import honeybadger
honeybadger.configure(api_key=config["honeybadger_api_key"])
app = Flask("LocalMailHandler", static_folder="src/static", template_folder="src/templates")

from src.mail import MailService

mail_service = MailService()


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

    # Checking if all data is valid
    if not config.valid_email(data["receiver"]):
        app.logger.error(f"400 error -> {request.path} by {request.remote_addr}, invalid receiver")
        return {"success": False, "status": 400, "message": "Invalid receiver email"}, 400

    # Check for existence of API key
    if not request.headers.get("API-KEY"):
        app.logger.error(f"400 error -> {request.path} by {request.remote_addr}, missing API key")
        return {"success": False, "status": 401,
                "message": "Missing API key. A header 'API-KEY' should be present."}, 401

    # Check for valid API key
    service = config.valid_api_key(request.headers.get("API-KEY"))
    if not service:
        app.logger.error(f"401 error -> {request.path} by {request.remote_addr}, invalid API key")
        return {"success": False, "status": 401, "message": "Unauthorized. Invalid API key."}, 401

    # Send mail
    mail_service.send_email(data["receiver"], data["subject"], data["body"])
    app.logger.info(
        f"200 status -> {service.upper()} {request.path} by {request.remote_addr}, sending email to "
        f"'{data['receiver']}' with subject '{data['subject']}' and body '{data['body']}'")

    return {"success": True, "status": 200, "message": "Message send."}, 200


@app.route("/mail/test/", methods=["POST"])
def mail_test():
    app.logger.info(
        f"200 status -> {request.path} by {request.remote_addr}, sending test email to '{config['mail']['recipient_email']}'")
    mail_service.send_email(config['mail']['recipient_email'], "LocalMailHandler Test",
                            "This is a test email, triggered by a post request to /mail/test/")
    return {"success": True, "status": 200, "message": "Test message sent."}, 200


def pretty_form_text(data: dict) -> str:
    result = "\n"
    for key, value in data.items():
        value = str(value).replace("\n", " ")
        result += f"{key}: {value}\n"
    return result


@app.route("/form/submit/", methods=["POST"])
def submit():
    if not request.form:
        app.logger.error(f"400 error -> {request.path} by {request.remote_addr}, no form data provided")
        return {"success": False, "status": 400, "message": "No form data provided"}, 400

    app.logger.info(f"200 status -> {request.path} by {request.remote_addr}, form data received: {request.form}")

    mail_service.send_email(config['mail']['recipient_email'], "Formular submitted",
f'''Hello there!

Someone has submitted a form with the following data:
{pretty_form_text(request.form)}
Kind regards,

Your friendly LocalMailHandler''')
    return {"success": True, "status": 200, "message": "Form submission successful."}, 200


@app.route("/server/status/", methods=["GET"])
def status():
    return {"success": True, "status": 200, "message": "Server is running."}, 200


@app.route("/", methods=["GET"])
def index():
    return render_template("docs/index.html")


@app.errorhandler(405)
def error405(error):
    app.logger.error(f"405 error -> {request.method} to {request.path} by {request.remote_addr}")
    return {"success": False, "status": 405, "message": f"Method {request.method} not allowed"}, 405


@app.errorhandler(404)
def error404(error):
    app.logger.error(f"404 error -> {request.path} by {request.remote_addr}")
    return {"success": False, "status": 404, "message": "Page not found."}, 404


@app.errorhandler(500)
def error500(error):
    app.logger.error(f"500 error -> {request.path} by {request.remote_addr}. Error: {error}")
    return {"success": False, "status": 500, "message": "Internal server error. Check the logs for more info."}, 500

from flask import Flask

import logging

app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    logging.info("404 error")
    return {"success": False, "status": 404, "message": "Page not found."}, 404
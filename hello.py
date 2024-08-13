from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    """
    Defines a route for the root URL ("/") of the application.

    Returns:
        str: A simple HTML paragraph containing the text "Hello, World!".
    """
    return "<p>Hello, World!</p>"

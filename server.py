from flask import Flask

from parameters import get_parameter

app = Flask(__name__)


@app.route('/')
def index() -> tuple:
    return 'All works!', 200


if __name__ == '__main__':
    app.run(debug=True, port=int(get_parameter('port')))

import os

from flask import Flask
from dotenv import load_dotenv

from routes import main_routes

root_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(root_dir, '.env'))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['secret_key']
app.config['SERVER_NAME'] = 'localhost:7777'
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '1000237797032383',
        'secret': '1607b1aebd91779669a6791c5270f215'
    },
    'twitter': {
        'id': '3RzWQclolxWZIMq5LJqzRZPTl',
        'secret': 'm9TEd58DSEtRrZHpz2EjrV9AhsBRxKMo8m3kuIZj3zLwzwIimt'
    }
}
app.register_blueprint(main_routes.main_bp)

if __name__ == '__main__':
    import logging

    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.DEBUG, datefmt='%m/%d/%Y %I:%M:%S %p')
    app.logger.setLevel(logging.DEBUG)
    # app.run()
    app.run(use_reloader=True, ssl_context='adhoc')

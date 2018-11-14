from flask import Flask, render_template, request, g
from flask_redis import FlaskRedis
import pandas as pd

from url_handlers.main import main_page
from url_handlers.log_plots import log_plots_page
from url_handlers.compare import compare_page
from url_handlers.heatmap import heatmap_page

app = Flask(__name__)

app.register_blueprint(main_page)
app.register_blueprint(log_plots_page)
app.register_blueprint(compare_page)
app.register_blueprint(heatmap_page)

# Database stuff
def connect_db():
    """ connects to our redis database """
    redis_store = FlaskRedis() # redis_store = FlaskRedis(decode_responses=True) # doesnt work for post request because of compressed shit.
    redis_store.init_app(app)
    return redis_store

def get_db():
    """ opens a new database connection if there is none yet for the
        current application context
    """
    if not hasattr(g, 'redis_db'):
        g.redis_db = connect_db()
    return g.redis_db

#
# @app.teardown_appcontext
# def close_db(error):
#     """ close the database, or whatever, on exit """
#     pass
#
# def init_db():
#     db = get_db()
#     return
#
#     # we can use app.open_resource to grab something from the main
#     # folder (flaskr, here)
#     with app.open_resource('schema.sql', mode='r') as f:
#         pass
#
# @app.cli.command('initdb')
# def initdb_command():
#     """ this function is associated with the "initdb" command of the
#         "flask" script
#     """
#     init_db()
from flask import Flask, render_template, request, g
from flask_redis import FlaskRedis
import pandas as pd

from url_handlers.main import main_page
from url_handlers.log_plots import log_plots_page
from url_handlers.compare import compare_page
from url_handlers.heatmap import heatmap_page
from url_handlers.data_import import import_page
from url_handlers.clustering import cluster_page

app = Flask(__name__)

app.register_blueprint(main_page)
app.register_blueprint(log_plots_page)
app.register_blueprint(compare_page)
app.register_blueprint(heatmap_page)
app.register_blueprint(import_page)
app.register_blueprint(cluster_page)

# Database stuff
def connect_db():
    """ connects to our redis database """
    redis_store = FlaskRedis()
    redis_store.init_app(app)
    return redis_store

def get_db():
    """ opens a new database connection if there is none yet for the
        current application context
    """
    if not hasattr(g, 'redis_db'):
        g.redis_db = connect_db()
    return g.redis_db

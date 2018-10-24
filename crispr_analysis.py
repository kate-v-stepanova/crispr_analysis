# import os
#
from flask import Flask, render_template, request, g
from flask_redis import FlaskRedis
import pandas as pd

from url_handlers.main import main_page
from url_handlers.log_plots import log_plots_page
from url_handlers.compare import compare_page

app = Flask(__name__)

# APP_ROOT = os.path.dirname(os.path.abspath(__file__))
# APP_STATIC = os.path.join(APP_ROOT, 'static')
# FINAL_TABLE = 'FinalTableM2.txt'
#
# # parse CSV file into pandas DataFrame
# ORIGINAL_DF = pd.read_csv(os.path.join(APP_STATIC, FINAL_TABLE), sep='\t')
# # replace NaN values with -1
# ORIGINAL_DF = ORIGINAL_DF.fillna(-1)
#
# # init cell_lines
# CELL_LINES = []
# for column in sorted(ORIGINAL_DF.columns[1:]):
#     if '_fc' in column:
#         cell_line = column.split('_fc')[0]
#         if cell_line not in CELL_LINES:
#             CELL_LINES.append(cell_line)
#
# GENES = ORIGINAL_DF['gene_id'].tolist()

app.register_blueprint(main_page)
app.register_blueprint(log_plots_page)
app.register_blueprint(compare_page)

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
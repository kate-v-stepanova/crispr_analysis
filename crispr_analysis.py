import os

from flask import Flask, render_template, request
import pandas as pd

from url_handlers.main import main_page
from url_handlers.log_plots import log_plots_page
from url_handlers.compare import compare_page

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')
FINAL_TABLE = 'FinalTableM2.txt'

# parse CSV file into pandas DataFrame
ORIGINAL_DF = pd.read_csv(os.path.join(APP_STATIC, FINAL_TABLE), sep='\t')
# replace NaN values with -1
ORIGINAL_DF = ORIGINAL_DF.fillna(-1)

# init cell_lines
CELL_LINES = []
for column in sorted(ORIGINAL_DF.columns[1:]):
    if '_fc' in column:
        cell_line = column.split('_fc')[0]
        if cell_line not in CELL_LINES:
            CELL_LINES.append(cell_line)

GENES = ORIGINAL_DF['gene_id'].tolist()

app.register_blueprint(main_page)
app.register_blueprint(log_plots_page)
app.register_blueprint(compare_page)

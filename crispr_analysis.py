import os

from flask import Flask, render_template, request
import pandas as pd

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

app.register_blueprint(log_plots_page)
app.register_blueprint(compare_page)

@app.route('/', methods=['GET', 'POST'])
def show_scatter_plot():
    if request.method == 'GET':
        return render_template('main.html', cell_lines=CELL_LINES)

    if request.method == 'POST':
        columns = ['gene_id', '{}_fc'.format(cell_line), '{}_pval'.format(cell_line)]
        df = ORIGINAL_DF[columns]
        p_values = request.form['p_values']

        # transforming to highcharts format
        df.columns = ['name', 'y', 'p_value']
        df.y.astype(float)
        df.p_value.astype(float)

        if p_values == 'display':
            plot_series = list(df.T.to_dict().values())

        if p_values == 'drop':
            # replace 0 with nans and drop nan from p_val columns
            df = df.replace(0, pd.np.nan).dropna(axis=0, how="any", subset=['p_value'])
            plot_series = list(df.T.to_dict().values())

        if p_values == 'highlight':
            zero_df = df.loc[df['y'] == 0]
            zero_df['name'] = pd.Series(cell_line)
            non_zero_df = df.loc[df['y'] != 0]
            non_zero_df['name'] = pd.Series('{}_with_zero_p_values'.format(cell_line))
            plot_series = list(non_zero_df.T.to_dict().values()) + list(zero_df.T.to_dict().values())

        return render_template('main.html', cell_lines=CELL_LINES, genes=GENES, plot_series=plot_series,
                               selected_cell_line=cell_line, p_values=p_values)

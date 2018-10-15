import os

from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')

@app.route('/')
def show_scatter_plot(methods=['GET', 'POST']):
    final_table = 'FinalTableM2.txt'
    df = pd.read_csv(os.path.join(APP_STATIC, final_table), sep='\t')

    # replace NaN values with -1
    df = df.fillna(-1)

    cell_lines = []
    genes = df['gene_id'].tolist()

    # {'MSH6': [ {y: fc_value, pvalue: pvalue} ]}
    plot_series = {}
    # excluding gene_id column
    for column in sorted(df.columns[1:]):
        if '_fc' in column:
            cell_line = column.split('_fc')[0]
            if cell_line not in cell_lines:
                cell_lines.append(cell_line)
            fc_column = column
            pval_column = cell_line + '_pval'
            if cell_line not in plot_series:
                plot_series[cell_line] = df[[fc_column, pval_column]]
                # transforming to highcharts format
                plot_series[cell_line].columns = ['y', 'value']
                plot_series[cell_line].y.astype(float)
                plot_series[cell_line].value.astype(float)
                plot_series[cell_line] = list(plot_series[cell_line].T.to_dict().values())
    return render_template('main.html', cell_lines=cell_lines, genes=genes, plot_series=plot_series)
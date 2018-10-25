import math

from flask import Blueprint, render_template, request
import pandas as pd


log_plots_page = Blueprint('log_plots', __name__)

@log_plots_page.route('/log_plots', methods=['GET', 'POST'])
def get_log_plots():
    from crispr_analysis import get_db
    rdb = get_db()
    cell_lines = rdb.smembers('cell_lines')
    cell_lines = [cell_line.decode('utf-8') for cell_line in cell_lines]

    if request.method == 'GET':
        return render_template('log_plots.html', cell_lines=cell_lines)

    if request.method == 'POST':
        cell_line = request.form['cell_line']
        df = pd.read_msgpack(rdb.get(cell_line))
        df = df[['gene_id', 'fc', 'pval']]

        genes = df['gene_id'].tolist()
        df['log_2_fc'] = df['fc'].apply(lambda x: math.log2(x))
        df['minus_log_10_pval'] = df['pval'].apply(lambda y: -math.log10(y) if y != 0 else -1)
        df.columns = ['gene_id', 'fc', 'pval', 'x', 'y']
        df = df.round(decimals=3)
        plot_series = [{
            'name': cell_line,
            'data': list(df.T.to_dict().values()),
            'turboThreshold': len(df)
        }]
        return render_template('log_plots.html', cell_lines=cell_lines, selected_cell_line=cell_line,
                               plot_series=plot_series, genes=genes)

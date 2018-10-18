import math

from flask import Blueprint, render_template, request

log_plots_page = Blueprint('log_plots', __name__)


@log_plots_page.route('/log_plots', methods=['GET', 'POST'])
def get_log_plots():
    from crispr_analysis import CELL_LINES, ORIGINAL_DF, GENES
    if request.method == 'GET':
        return render_template('log_plots.html', cell_lines=CELL_LINES)

    if request.method == 'POST':
        cell_line = request.form['cell_line']
        fc_column = '{}_fc'.format(cell_line)
        pval_column = '{}_pval'.format(cell_line)
        columns = ['gene_id', fc_column, pval_column]
        df = ORIGINAL_DF[columns]
        df['log_2_fc'] = df[fc_column].apply(lambda x: math.log2(x))
        df['minus_log_10_pval'] = df[pval_column].apply(lambda y: math.log10(y) if y != 0 else -9)
        df.columns = ['name', 'fc', 'pval', 'x', 'y']
        df = df.round(decimals=3)
        plot_series = list(df.T.to_dict().values())
        return render_template('log_plots.html', cell_lines=CELL_LINES, selected_cell_line=cell_line,
                               plot_series=plot_series, genes=GENES)

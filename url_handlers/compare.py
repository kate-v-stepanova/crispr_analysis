import math

from flask import Blueprint, render_template, request

compare_page = Blueprint('compare', __name__)


@compare_page.route('/compare', methods=['GET', 'POST'])
def compare_cell_lines():
    from crispr_analysis import CELL_LINES, ORIGINAL_DF
    if request.method == 'GET':
        return render_template('compare.html', cell_lines=CELL_LINES)

    if request.method == 'POST':
        x_axis = request.form['x_axis']
        y_axis_multiple = request.form.getlist('y_axis_multiple')
        # here it doesn't matter how to plot, the data will be the same
        how_to_plot = request.form['how_to_plot']
        plot_series = {}
        for cell_line in y_axis_multiple:
            columns = ['gene_id', '{}_fc'.format(x_axis), '{}_fc'.format(cell_line),
                       '{}_pval'.format(x_axis), '{}_pval'.format(cell_line)]
            df = ORIGINAL_DF[columns]
            df.columns = ['gene_id', 'x', 'y', 'x_pval', 'y_pval']
            df = df.round(decimals=3)
            plot_series[cell_line] = {
                'name': '{} vs {}'.format(x_axis, cell_line),
                'data': list(df.T.to_dict().values()),
                'turboThreshold': len(df)
            }
        return render_template('compare.html', cell_lines=CELL_LINES, x_axis=x_axis, y_axis_multiple=y_axis_multiple,
                               plot_series=plot_series, how_to_plot=how_to_plot)

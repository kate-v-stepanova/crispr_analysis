import math

import pandas as pd
from flask import Blueprint, render_template, request

compare_page = Blueprint('compare', __name__)


@compare_page.route('/compare', methods=['GET', 'POST'])
def compare_cell_lines():
    from crispr_analysis import get_db
    rdb = get_db()

    cell_lines = rdb.smembers('cell_lines')
    cell_lines = [cell_line.decode('utf-8') for cell_line in cell_lines]

    if request.method == 'GET':
        return render_template('compare.html', cell_lines=cell_lines)

    if request.method == 'POST':
        x_axis = request.form.get('x_axis')
        y_axis_multiple = request.form.getlist('y_axis_multiple')

        x_axis_df = pd.read_msgpack(rdb.get(x_axis))
        x_axis_df = x_axis_df[['gene_id', 'fc', 'pval']]
        x_axis_df.columns = ['gene_id', 'x', 'x_pval']

        # here it doesn't matter how to plot, the data will be the same
        how_to_plot = request.form.get('how_to_plot')
        plot_series = {}
        show_data_table = request.form.get('show_data_table') is not None
        if show_data_table:
            data_table = x_axis_df.copy()
            data_table.columns = ['gene_id', '{}_fc'.format(x_axis), '{}_pval'.format(x_axis)]
        for cell_line in y_axis_multiple:
            y_axis_df = pd.read_msgpack(rdb.get(cell_line))
            y_axis_df = y_axis_df[['gene_id', 'fc', 'pval']]
            y_axis_df.columns = ['gene_id', 'y', 'y_pval']
            df = pd.concat([x_axis_df, y_axis_df])
            df = df.round(decimals=3)

            # add to data_table
            if show_data_table:
                y_axis_df.columns = ['gene_id', '{}_fc'.format(cell_line), '{}_pval'.format(cell_line)]
                data_table = pd.concat([data_table, y_axis_df]) # todo: maybe need to copy y_axis_df
            # apply filters
            apply_filters = request.form.get('apply_filters') is not None
            if apply_filters:
                x_fc = float(request.form.get('x_fc_max'))
                x_fc_less_or_greater = request.form.get('x_fc_less_or_greater')
                x_pval = float(request.form.get('x_pval_max'))
                x_pval_less_or_greater = request.form.get('x_pval_less_or_greater')
                y_fc = float(request.form.get('y_fc_max'))
                y_fc_less_or_greater = request.form.get('y_fc_less_or_greater')
                y_pval = float(request.form.get('y_pval_max'))
                y_pval_less_or_greater = request.form.get('y_pval_less_or_greater')
                df = df.loc[df['x'] >= x_fc] if x_fc_less_or_greater == 'greater' else df.loc[df['x'] <= x_fc]
                df = df.loc[df['y'] >= y_fc] if y_fc_less_or_greater == 'greater' else df.loc[df['y'] <= y_fc]
                df = df.loc[df['x_pval'] >= x_pval] if x_pval_less_or_greater == 'greater' else df.loc[df['x_pval'] <= x_pval]
                df = df.loc[df['y_pval'] >= y_pval] if y_pval_less_or_greater == 'greater' else df.loc[df['y_pval'] <= y_pval]

            plot_series[cell_line] = {
                'name': '{}'.format(cell_line),
                'data': list(df.T.to_dict().values()),
                'turboThreshold': len(df)
            }
        if show_data_table:
            data_table = {'header': data_table.columns, 'rows': data_table.values.tolist()}

        return render_template('compare.html', cell_lines=cell_lines, x_axis=x_axis, y_axis_multiple=y_axis_multiple,
                               plot_series=plot_series, how_to_plot=how_to_plot, data_table=data_table)
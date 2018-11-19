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

        # here it doesn't matter how to plot, the data will be the same
        how_to_plot = request.form.get('how_to_plot')
        show_data_table = request.form.get('show_data_table') is not None

        # filters
        apply_filters = request.form.get('apply_filters') is not None
        wt_fc_max = float(request.form.get('wt_fc_max'))
        wt_fc_min = float(request.form.get('wt_fc_min'))
        wt_pval = float(request.form.get('wt_pval_max'))
        wt_pval_less_or_greater = request.form.get('wt_pval_less_or_greater')
        fc_max = float(request.form.get('y_fc_max'))
        fc_min = float(request.form.get('y_fc_min'))
        pval = float(request.form.get('y_pval_max'))
        pval_less_or_greater = request.form.get('y_pval_less_or_greater')


        x_axis_df = pd.read_msgpack(rdb.get(x_axis))
        x_axis_df = x_axis_df[['gene_id', 'fc', 'pval']]
        x_axis_df.columns = ['gene_id', 'x', 'x_pval']
        x_axis_df = x_axis_df.round(decimals=3)

        if apply_filters:
            if x_axis == 'WT':
                x_axis_df = x_axis_df.loc[x_axis_df['x'] <= wt_fc_max]
                x_axis_df = x_axis_df.loc[x_axis_df['x'] >= wt_fc_min]
                x_axis_df = x_axis_df.loc[x_axis_df['x_pval'] >= wt_pval] if wt_pval_less_or_greater == 'greater' else \
                            x_axis_df.loc[x_axis_df['x_pval'] <= wt_pval]
            else:
                x_axis_df = x_axis_df.loc[x_axis_df['x'] <= fc_max]
                x_axis_df = x_axis_df.loc[x_axis_df['x'] >= fc_min]
                x_axis_df = x_axis_df.loc[x_axis_df['x_pval'] >= pval] if pval_less_or_greater == 'greater' else \
                            x_axis_df.loc[x_axis_df['x_pval'] <= pval]

        joint_df = None
        full_df = None
        for cell_line in y_axis_multiple:
            df = pd.read_msgpack(rdb.get(cell_line))
            df = df[['gene_id', 'fc', 'pval', 'inc_ess']]
            df.fc.astype(float)
            df.pval.astype(float)

            if show_data_table:
                # to fill the data table correctly
                to_merge = df.copy() if cell_line != 'WT' else df[['gene_id', 'fc', 'pval']].copy()
                to_merge = to_merge.round(decimals=3)
                columns = ['gene_id', '{}_fc'.format(cell_line), '{}_pval'.format(cell_line)]
                if cell_line != 'WT':
                    columns.append('{}_inc_ess'.format(cell_line))
                to_merge.columns = columns
                full_df = to_merge if full_df is None else pd.merge(full_df, to_merge, how='outer', on='gene_id')


            # apply_filters
            if apply_filters:
                if cell_line == 'WT':
                    df = df.loc[df['fc'] >= wt_fc_min]
                    df = df.loc[df['fc'] <= wt_fc_max]
                    df = df.loc[df['pval'] >= wt_pval] if wt_pval_less_or_greater == 'greater' else df.loc[df['pval'] <= wt_pval]
                else:
                    df = df.loc[df['fc'] >= fc_min]
                    df = df.loc[df['fc'] <= fc_max]
                    df = df.loc[df['pval'] >= pval] if pval_less_or_greater == 'greater' else df.loc[df['pval'] <= pval]

            df = df.round(decimals=3)

            df.columns = ['gene_id', '{}_fc'.format(cell_line), '{}_pval'.format(cell_line),
                    '{}_inc_ess'.format(cell_line)]
            joint_df = df.copy() if joint_df is None else pd.merge(joint_df, df, how='outer', on='gene_id')

        plot_series = []
        for cell_line in y_axis_multiple:
            df = joint_df[['gene_id', '{}_fc'.format(cell_line),
                           '{}_pval'.format(cell_line), '{}_inc_ess'.format(cell_line)]]
            df.columns = ['gene_id', 'y', 'y_pval', 'inc_ess']
            df = pd.merge(df, x_axis_df, how='inner', on='gene_id')
            series_length = len(df.dropna())
            # df = df.fillna('null')
            df = df.dropna()
            plot_series.append({
                'name': cell_line,
                'data': list(df.T.to_dict().values()),
                'turboThreshold': len(df),
                'series_length': series_length
            })

        data_table = None
        if show_data_table:
            genes = joint_df['gene_id'].tolist()
            data_table_df = full_df[full_df['gene_id'].isin(genes)]
            x_columns = ['gene_id', '{}_fc'.format(x_axis), '{}_pval'.format(x_axis)]
            if x_axis != 'WT':
                x_columns.append('{}_inc_ess'.format(x_axis))
            x_axis_df.columns = x_columns
            data_table_df = pd.merge(data_table_df, x_axis_df, how='inner', on='gene_id')

            data_table_df.insert(0, '#', range(1, len(data_table_df)+1))
            data_table = {
                'header': data_table_df.columns,
                'rows': data_table_df.values.tolist(),
                'csv': data_table_df.to_csv(sep='\t', index=False)
            }


        return render_template('compare.html', cell_lines=cell_lines, x_axis=x_axis, y_axis_multiple=y_axis_multiple,
                               plot_series=plot_series, how_to_plot=how_to_plot, data_table=data_table, apply_filters=apply_filters)
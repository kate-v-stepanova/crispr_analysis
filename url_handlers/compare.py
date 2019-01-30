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
        x_fc_max = float(request.form.get('x_fc_max'))
        # x_fc_min = float(request.form.get('x_fc_min'))
        x_pval = float(request.form.get('x_pval'))
        x_pval_less_or_greater = request.form.get('x_pval_less_or_greater')
        y_fc_max = float(request.form.get('y_fc_max'))
        # y_fc_min = float(request.form.get('y_fc_min'))
        y_pval = float(request.form.get('y_pval'))
        y_pval_less_or_greater = request.form.get('y_pval_less_or_greater')

        x_axis_df = pd.read_msgpack(rdb.get(x_axis))
        x_axis_df = x_axis_df[['gene_id', 'fc', 'pval']]
        x_axis_df.columns = ['gene_id', 'x', 'x_pval']
        x_axis_df = x_axis_df.round(decimals=3)
        #
        if apply_filters:
            x_axis_df = x_axis_df.loc[x_axis_df['x'] <= x_fc_max]
            # x_axis_df = x_axis_df.loc[x_axis_df['x'] >= x_fc_min]
            x_axis_df = x_axis_df.loc[x_axis_df['x_pval'] >= x_pval] if x_pval_less_or_greater == 'greater' else \
                        x_axis_df.loc[x_axis_df['x_pval'] <= x_pval]

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

            if apply_filters:
                # if 'WT' in cell_line:
                #     # df = df.loc[df['fc'] >= x_fc_min]
                #     df = df.loc[df['fc'] <= x_fc_max]
                #     df = df.loc[df['pval'] >= x_pval] if x_pval_less_or_greater == 'greater' \
                #         else df.loc[df['pval'] <= x_pval]
                #     # df = df.loc[df['fc'] >= x_fc_min]
                #     # df = df.loc[df['fc'] <= x_fc_max]
                #     # df = df.loc[df['pval'] >= x_pval] if x_pval_less_or_greater == 'greater' \
                #     #     else df.loc[df['pval'] <= x_pval]
                # else:
                    # df = df.loc[df['fc'] >= y_fc_min]
                    df = df.loc[df['fc'] <= y_fc_max]
                    df = df.loc[df['pval'] >= y_pval] if y_pval_less_or_greater == 'greater' \
                        else df.loc[df['pval'] <= y_pval]
                    # df = df.loc[df['fc'] >= y_fc_min]
                    # df = df.loc[df['fc'] <= y_fc_max]
                    # df = df.loc[df['pval'] >= y_pval] if y_pval_less_or_greater == 'greater' \
                    #     else df.loc[df['pval'] <= y_pval]


            df = df.round(decimals=3)

            df.columns = ['gene_id', '{}_fc'.format(cell_line), '{}_pval'.format(cell_line),
                    '{}_inc_ess'.format(cell_line)]
            joint_df = df.copy() if joint_df is None else pd.merge(joint_df, df, how='outer', on='gene_id')
        #
        # # apply_filters
        # if apply_filters:
        #     for cell_line in cell_lines:
        #     wt_df = joint_df.loc[(joint_df["cell_line"].str.contains('WT')) & (joint_df["fc"] <= x_fc_max)]
        #     wt_df = wt_df.loc[wt_df['pval'] >= x_pval] if x_pval_less_or_greater == 'greater' \
        #         else wt_df.loc[wt_df['pval'] <= x_pval]
        #     df = joint_df.loc[(not joint_df["cell_line"].str.contains('WT')) & (joint_df["fc"] <= y_fc_max)]
        #     df = df.loc[df['pval'] >= y_pval] if y_pval_less_or_greater == 'greater' \
        #         else df.loc[df['pval'] <= y_pval]
        #     joint_df = pd.merge(df, wt_df, how='inner', on='gene_id')


        plot_series = []
        for cell_line in y_axis_multiple:

            df = joint_df[['gene_id', '{}_fc'.format(cell_line),
                           '{}_pval'.format(cell_line), '{}_inc_ess'.format(cell_line)]]

            df.columns = ['gene_id', 'y', 'y_pval', 'inc_ess']
            df = pd.merge(df, x_axis_df, how='outer', on='gene_id')
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
            if 'WT' not in x_axis:
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
                               plot_series=plot_series, how_to_plot=how_to_plot, data_table=data_table, apply_filters=apply_filters,
                               selected_filter={
                                    'x_fc_max': x_fc_max,
                                    # 'x_fc_min': x_fc_min,
                                    'x_pval': x_pval,
                                    'x_pval_less_or_greater': x_pval_less_or_greater,
                                    'y_fc_max': y_fc_max,
                                    'y_pval': y_pval,
                                    'y_pval_less_or_greater': y_pval_less_or_greater,
                               })



# js post request - called on selected an entity from a list
@compare_page.route('/get_norm_counts/<gene>/<cell_lines>', methods=['POST'])
def get_norm_counts(gene, cell_lines):
    # this import has to be here!!
    from crispr_analysis import get_db
    rdb = get_db()
    cell_lines = cell_lines.split(',')
    msgpack = rdb.get('{}_counts'.format(gene))
    if msgpack is None:
        return jsonify({
            'data': [],
            'errors': ['No counts for gene {} found'.format(gene)]
        })
    gene_df = pd.read_msgpack(msgpack)
    series_before = []
    series_after = []
    outliers = []
    error_messages = []
    for i in range(len(cell_lines)):
        cell_line = cell_lines[i]
        # key = 'RPE_{}'.format(cell_line)
        df = gene_df.loc[gene_df['cell_line'] == cell_line]
        # if df.empty:
        #     key = cell_line
        #     df = gene_df.loc[gene_df['cell_line'] == key]
        if df.empty:
            error_messages.append('No counts for gene: {} and cell line: {}. '.format(gene, cell_line))
            continue

        # keep only the ones that are within +3 to -3 standard deviations
        without_outliers = df[np.abs(df.norm_counts - df.norm_counts.mean()) <= (3 * df.norm_counts.std())]
        only_outliers = df[np.abs(df.norm_counts - df.norm_counts.mean()) > (3 * df.norm_counts.std())]
        before = without_outliers.loc[without_outliers['treatment'] == 0]
        after = without_outliers.loc[without_outliers['treatment'] == 1]

        # calculate boxplot data
        q1, median, q3 = before.norm_counts.quantile([0.25, 0.5, 0.75]).round(decimals=3).tolist()
        series_before.append([
            before['norm_counts'].min().round(decimals=3),
            q1,
            median,
            q3,
            before['norm_counts'].max().round(decimals=3)])
        q1, median, q3 = after.norm_counts.quantile([0.25, 0.5, 0.75]).round(decimals=3).tolist()
        series_after.append([
                after['norm_counts'].min().round(decimals=3),
                q1,
                median,
                q3,
                after['norm_counts'].max().round(decimals=3)])
        for index, row in only_outliers.iterrows():
            x = i
            y = round(row['norm_counts'], 3)
            treatment = 'Before Treatment' if int(row['treatment']) == 0 else 'After Treatment'
            outliers.append({
                'x': x,
                'y': y,
                'treatment': treatment,
                'cell_line': cell_line,
                'color': 'black' if treatment == 'After Treatment' else '#7cb5ec'
            })

    counts_series = [{
            'name': 'Before Treatment',
            'data': series_before,
            'color': '#7cb5ec',
        }, {
            'name': 'After Treatment',
            'data': series_after,
            'color': 'black',
        }, {'name': 'Outliers',
            'type': 'scatter',
            'data': outliers,
            'color': 'black',
            'tooltip': {
                'pointFormat': '<br>cell line: {point.cell_line}<br>norm. counts: {point.y}<br>treatment: {point.treatment}',
            }
        }
    ]
    return jsonify({
        'data': counts_series,
        'errors': error_messages,
    })

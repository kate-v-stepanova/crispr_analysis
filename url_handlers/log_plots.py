import math

from flask import Blueprint, render_template, request
import pandas as pd
import numpy as np


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

        #  dash lines
        left = float(request.form.get('left'))
        right = float(request.form.get('right'))
        bottom = float(request.form.get('bottom'))

        left_line = round(math.log2(left), 2)
        right_line = round(math.log2(right), 2)
        bottom_line = -round(math.log10(bottom), 2)

        genes = df['gene_id'].tolist()
        df['log_2_fc'] = df['fc'].apply(lambda x: math.log2(x))
        df['minus_log_10_pval'] = df['pval'].apply(lambda y: -math.log10(y) if y != 0 else np.nan)

        df = df.round(decimals=3)
        max_val = df['minus_log_10_pval'].max().round(decimals=3)

        df.columns = ['gene_id', 'fc', 'pval', 'x', 'y']
        left_df = df.loc[(df['fc'] <= left) & (df['pval'] <=bottom)]
        right_df = df.loc[(df['fc'] >= right) & (df['pval'] <=bottom)]
        bottom_df = df[~df.isin(left_df) & ~df.isin(right_df)].dropna()
        right_df = right_df.fillna(max_val+0.5)
        left_df = left_df.fillna(max_val+0.5)
        plot_series = [{
                'name': cell_line,
                'data': list(bottom_df.dropna().T.to_dict().values()),
                'turboThreshold': len(bottom_df),
                'marker': {
                    'symbol': 'circle',
                    'radius': 5,
                },
                'color': 'grey',
            },
            {
                'name': cell_line,
                'data': list(left_df.dropna().T.to_dict().values()),
                'turboThreshold': len(left_df),
                'color': 'blue',
                'marker': {
                    'symbol': 'circle',
                    'radius': 5,
                },
            },
            {
                'name': cell_line,
                'data': list(right_df.dropna().T.to_dict().values()),
                'turboThreshold': len(right_df),
                'color': 'red',
                'marker': {
                    'symbol': 'circle',
                    'radius': 5,
                },
        }]

        # # # it slows down the page too much
        # # data for normalized counts
        # counts_series = {}
        # for gene in genes:
        #     gene_df = pd.read_msgpack(rdb.get('{}_counts'.format(gene)))
        #     series_before = []
        #     series_after = []
        #     outliers = []
        #     key = 'RPE_{}'.format(cell_line)
        #     df = gene_df.loc[gene_df['cell_line'] == key]
        #
        #     # keep only the ones that are within +3 to -3 standard deviations
        #     without_outliers = df[np.abs(df.norm_counts - df.norm_counts.mean()) <= (3 * df.norm_counts.std())]
        #     only_outliers = df[np.abs(df.norm_counts - df.norm_counts.mean()) > (3 * df.norm_counts.std())]
        #     before = without_outliers.loc[without_outliers['treatment'] == 0]
        #     after = without_outliers.loc[without_outliers['treatment'] == 1]
        #
        #     # calculate boxplot data
        #     q1, median, q3 = before.norm_counts.quantile([0.25, 0.5, 0.75]).round(decimals=3).tolist()
        #     series_before.append([
        #         before['norm_counts'].min(),
        #         q1,
        #         median,
        #         q3,
        #         before['norm_counts'].max()])
        #     q1, median, q3 = after.norm_counts.quantile([0.25, 0.5, 0.75]).tolist()
        #     series_after.append([
        #         after['norm_counts'].min(),
        #         q1,
        #         median,
        #         q3,
        #         after['norm_counts'].max()])
        #     for index, row in only_outliers.iterrows():
        #         i=0
        #         x = i
        #         y = round(row['norm_counts'], 3)
        #         treatment = 'Before Treatment' if int(row['treatment']) == 0 else 'After Treatment'
        #         outliers.append({
        #             'x': x,
        #             'y': y,
        #             'treatment': treatment,
        #             'cell_line': cell_line,
        #             'color': 'black' if treatment == 'After Treatment' else '#7cb5ec'
        #         })
        #     counts_series[gene] = [{
        #         'name': 'Before Treatment',
        #         'data': series_before,
        #         'color': '#7cb5ec',
        #     }, {
        #         'name': 'After Treatment',
        #         'data': series_after,
        #         'color': 'black',
        #     }, {'name': 'Outliers',
        #         'type': 'scatter',
        #         'data': outliers,
        #         'color': 'black',
        #         'tooltip': {
        #             'pointFormat': '<br>cell line: {point.cell_line}<br>norm. counts: {point.y}<br>treatment: {point.treatment}',
        #         }
        #         }
        #     ]
        return render_template('log_plots.html', cell_lines=cell_lines, selected_cell_line=cell_line,
                               plot_series=plot_series, genes=genes, right=right_line, left=left_line, bottom=bottom_line,
                               selected_thresholds = {
                                   'left': left,
                                   'right': right,
                                   'bottom': bottom,
                               }
                               )

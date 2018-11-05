import math

from flask import Blueprint, render_template, request
import pandas as pd
import numpy as np

main_page = Blueprint('main', __name__)

@main_page.route('/', methods=['GET', 'POST'])
def show_scatter_plot():
    from crispr_analysis import get_db
    rdb = get_db()

    cell_lines = rdb.smembers('cell_lines')

    # I don't like the idea of manually fixing the strings, but I couldn't find a better way
    cell_lines = [cell_line.decode('utf-8') for cell_line in cell_lines]

    if request.method == 'GET':
        return render_template('main.html', cell_lines=cell_lines)

    if request.method == 'POST':
        selected_cell_lines = request.form.getlist('cell_lines')
        increased_essentiality = request.form.get('increased_essentiality') is not None
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

        joint_df = None
        wt_df = None
        full_df = None
        for cell_line in selected_cell_lines:
            df = pd.read_msgpack(rdb.get(cell_line))
            df = df[['gene_id', 'fc', 'pval', 'inc_ess']]
            df.fc.astype(float)
            df.pval.astype(float)

            if show_data_table:
                # to fill the data table correctly
                to_merge = df.copy() if cell_line != 'WT' else df[['gene_id', 'fc', 'pval']]
                to_merge = to_merge.round(decimals=3)
                columns = ['gene_id', '{}_fc'.format(cell_line), '{}_pval'.format(cell_line)]
                if cell_line != 'WT':
                    columns.append('{}_inc_ess'.format(cell_line))
                to_merge.columns = columns
                full_df = to_merge if full_df is None else pd.merge(full_df, to_merge, how='outer', on='gene_id')

            if increased_essentiality:
                # this will also include 'n/a'
                df = df.loc[df['inc_ess'] != 'no']
                # not sure yet how to handle series without these genes
                # df = df.fillna('null')
                # df = df.dropna()

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

            if cell_line == 'WT':
                df['WT_inc_ess'] = 'n/a'
                wt_df = df
            else:
                joint_df = df.copy() if joint_df is None else pd.merge(joint_df, df, how='outer', on='gene_id')

        if wt_df is not None:
            joint_df = pd.merge(joint_df, wt_df, how='inner', on='gene_id')
        genes = list(joint_df['gene_id'])

        plot_series = []
        for cell_line in selected_cell_lines:
            df = joint_df[['gene_id', '{}_fc'.format(cell_line),
                           '{}_pval'.format(cell_line), '{}_inc_ess'.format(cell_line)]]
            df.columns = ['name', 'y', 'pval', 'inc_ess']
            series_length = len(df.dropna())
            df = df.fillna('null')
            plot_series.append({
                'name': cell_line,
                'turboThreshold': len(df),
                'data': list(df.T.to_dict().values()),
                'series_length': series_length
            })

        data_table = None
        if show_data_table:
            genes = joint_df['gene_id'].tolist()
            data_table_df = full_df[full_df['gene_id'].isin(genes)]
            data_table = {
                'header': data_table_df.columns,
                'rows': data_table_df.values.tolist(),
                'csv': data_table_df.to_csv(sep='\t', index=False)
            }

        # data for normalized counts
        counts_series = {}
        for gene in genes:
            gene_df = pd.read_msgpack(rdb.get('{}_counts'.format(gene)))
            series_before = []
            series_after = []
            outliers = []
            for i in range(len(selected_cell_lines)):
                cell_line = selected_cell_lines[i]
                key = 'RPE_{}'.format(cell_line)
                df = gene_df.loc[gene_df['cell_line'] == key]

                # keep only the ones that are within +3 to -3 standard deviations
                without_outliers = df[np.abs(df.norm_counts - df.norm_counts.mean()) <= (3 * df.norm_counts.std())]
                only_outliers = df[np.abs(df.norm_counts - df.norm_counts.mean()) > (3 * df.norm_counts.std())]
                before = without_outliers.loc[without_outliers['treatment'] == 0]
                after = without_outliers.loc[without_outliers['treatment'] == 1]

                # calculate boxplot data
                q1, median, q3 = before.norm_counts.quantile([0.25, 0.5, 0.75]).round(decimals=3).tolist()
                series_before.append([
                    before['norm_counts'].min(),
                    q1,
                    median,
                    q3,
                    before['norm_counts'].max()])
                q1, median, q3 = after.norm_counts.quantile([0.25, 0.5, 0.75]).tolist()
                series_after.append([
                        after['norm_counts'].min(),
                        q1,
                        median,
                        q3,
                        after['norm_counts'].max()])
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
            counts_series[gene] = [{
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
        return render_template('main.html', cell_lines=cell_lines, genes=genes, plot_series=plot_series,
                               selected_cell_lines=selected_cell_lines, data_table=data_table, counts_series=counts_series,
                               increased_essentiality=increased_essentiality, apply_filters=apply_filters)
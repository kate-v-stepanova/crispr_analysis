from flask import Blueprint, render_template, request
import pandas as pd
import numpy as np

heatmap_page = Blueprint('heatmap', __name__)

@heatmap_page.route('/heatmap', methods=['GET', 'POST'])
def show_heatmap():

    from crispr_analysis import get_db
    rdb = get_db()
    cell_lines = rdb.smembers('cell_lines')

    # I don't like the idea of manually fixing the strings, but I couldn't find a better way
    cell_lines = [cell_line.decode('utf-8') for cell_line in cell_lines]

    if request.method == 'POST':
        selected_cell_lines = request.form.getlist('cell_lines')
        selected_genes = request.form.get('selected_genes').strip().split()
        joint_df = None
        for cell_line in selected_cell_lines:
            df = pd.read_msgpack(rdb.get(cell_line))
            df = df[['gene_id', 'fc', 'pval', 'inc_ess']]
            if cell_line == 'WT':
                df['inc_ess'] = 'n/a'
            df.fc.astype(float)
            df.pval.astype(float)
            df.columns = ['gene_id', '{}_fc'.format(cell_line), '{}_pval'.format(cell_line), '{}_inc_ess'.format(cell_line)]

            if joint_df is None:
                joint_df = df.copy()
            else:
                joint_df = pd.merge(joint_df, df, how='outer', on='gene_id')

        joint_df = joint_df.loc[joint_df['gene_id'].isin(selected_genes)].reset_index()
        joint_df = joint_df.round(decimals=3)
        plot_series = []
        for i, row in joint_df.iterrows():
            for cell_line in selected_cell_lines:
                plot_series.append({
                    'x': selected_cell_lines.index(cell_line),
                    'y': i,
                    'cell_line': cell_line,
                    'gene_id': row['gene_id'],
                    'pval': row['{}_pval'.format(cell_line)],
                    'fc': row['{}_fc'.format(cell_line)],
                    'value': row['{}_fc'.format(cell_line)],
                    'inc_ess': row['{}_inc_ess'.format(cell_line)]
                })

        # to keep the order of genes
        selected_genes=joint_df['gene_id'].tolist()

        return render_template('heatmap.html', cell_lines=cell_lines, selected_cell_lines=selected_cell_lines,
                               selected_genes=selected_genes, plot_series=plot_series)

    return render_template('heatmap.html', cell_lines=cell_lines)



# js post request - called on selected an entity from a list
@heatmap_page.route('/get_norm_counts/<gene>/<cell_lines>', methods=['POST'])
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



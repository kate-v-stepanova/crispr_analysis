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


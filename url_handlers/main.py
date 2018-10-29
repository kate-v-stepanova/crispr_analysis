import math

from flask import Blueprint, render_template, request
import pandas as pd

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
        for cell_line in selected_cell_lines:
            df = pd.read_msgpack(rdb.get(cell_line))
            df = df[['gene_id', 'fc', 'pval', 'inc_ess']]
            df.fc.astype(float)
            df.pval.astype(float)

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

        return render_template('main.html', cell_lines=cell_lines, genes=genes, plot_series=plot_series,
                               selected_cell_lines=selected_cell_lines)
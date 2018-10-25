import math

from flask import Blueprint, render_template, request
import pandas as pd

main_page = Blueprint('main', __name__)

@main_page.route('/', methods=['GET', 'POST'])
def show_scatter_plot():
    from crispr_analysis import get_db
    rdb = get_db()


    cell_lines = rdb.smembers('cell_lines')
    genes = rdb.smembers('genes')

    # I don't like the idea of manually fixing the strings, but I couldn't find a better way
    cell_lines = [cell_line.decode('utf-8') for cell_line in cell_lines]
    genes = [gene.decode('utf-8') for gene in genes] # 13 thousand lines!!!

    if request.method == 'GET':
        return render_template('main.html', cell_lines=cell_lines)

    if request.method == 'POST':
        selected_cell_lines = request.form.getlist('cell_lines')

        # filters
        apply_filters = request.form.get('apply_filters') is not None
        wt_fc = float(request.form.get('wt_fc_max'))
        wt_fc_less_or_greater = request.form.get('wt_fc_less_or_greater')
        wt_pval = float(request.form.get('wt_pval_max'))
        wt_pval_less_or_greater = request.form.get('wt_pval_less_or_greater')
        fc = float(request.form.get('y_fc_max'))
        fc_less_or_greater = request.form.get('y_fc_less_or_greater')
        pval = float(request.form.get('y_pval_max'))
        pval_less_or_greater = request.form.get('y_pval_less_or_greater')

        plot_series = []
        for cell_line in selected_cell_lines:
            df = pd.read_msgpack(rdb.get(cell_line))
            df = df[['gene_id', 'fc', 'pval', 'inc_ess']]
            if cell_line == 'WT':
                df['inc_ess'] = 'n/a'
            # transforming to highcharts format
            df.columns = ['name', 'y', 'p_value', 'inc_ess']
            df.y.astype(float)
            df.p_value.astype(float)

            # apply_filters
            if apply_filters:
                if cell_line == 'WT':
                    df = df.loc[df['y'] >= wt_fc] if wt_fc_less_or_greater == 'greater' else df.loc[df['y'] <= wt_fc]
                    df = df.loc[df['p_value'] >= wt_pval] if wt_pval_less_or_greater == 'greater' else df.loc[df['p_value'] <= wt_pval]
                else:
                    df = df.loc[df['y'] >= fc] if fc_less_or_greater == 'greater' else df.loc[df['y'] <= fc]
                    df = df.loc[df['p_value'] >= pval] if pval_less_or_greater == 'greater' else df.loc[df['p_value'] <= pval]

            # todo: intersection
            df = df.round(decimals=3)
            plot_series.append({
                'name': cell_line,
                'turboThreshold': len(df),
                'data': list(df.T.to_dict().values())
            })

        return render_template('main.html', cell_lines=cell_lines, genes=genes, plot_series=plot_series,
                               selected_cell_lines=selected_cell_lines)
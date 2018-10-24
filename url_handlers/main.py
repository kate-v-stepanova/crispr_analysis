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

    # stupid shit I don't want to do it why the fuck it doesnt return normal strings
    cell_lines = [cell_line.decode('utf-8') for cell_line in cell_lines]
    genes = [gene.decode('utf-8') for gene in genes] # 13 thousand lines

    if request.method == 'GET':
        return render_template('main.html', cell_lines=cell_lines)

    if request.method == 'POST':
        cell_line = request.form.get('cell_line')
        df = pd.read_msgpack(rdb.get(cell_line))

        df = df[['gene_id', 'fc', 'pval']] #, 'inc_ess']
        p_values = request.form['p_values']

        # transforming to highcharts format
        df.columns = ['name', 'y', 'p_value']
        df.y.astype(float)
        df.p_value.astype(float)
        df = df.round(decimals=3)

        if p_values == 'highlight':
            zero_df = df.loc[df['p_value'] == 0]
            non_zero_df = df.loc[df['p_value'] != 0]
            plot_series = [{
                'name': cell_line,
                'turboThreshold': len(non_zero_df),
                'data': list(non_zero_df.T.to_dict().values())
            }, {
                'name': '{} with zero p_values'.format(cell_line),
                'turboThreshold': len(zero_df),
                'data': list(zero_df.T.to_dict().values())
            }]

        if p_values == 'display_only':
            df = df.loc[df['p_value'] == 0]
            plot_series = {
                'name': cell_line,
                'turboThreshold': len(df),
                'data': list(df.T.to_dict().values())
            }


        return render_template('main.html', cell_lines=cell_lines, genes=genes, plot_series=plot_series,
                               selected_cell_line=cell_line, p_values=p_values)


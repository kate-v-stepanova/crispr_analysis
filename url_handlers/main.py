import math

from flask import Blueprint, render_template, request

main_page = Blueprint('main', __name__)

@main_page.route('/', methods=['GET', 'POST'])
def show_scatter_plot():
    from crispr_analysis import CELL_LINES, ORIGINAL_DF, GENES

    if request.method == 'GET':
        return render_template('main.html', cell_lines=CELL_LINES)

    if request.method == 'POST':
        cell_line = request.form.get('cell_line')
        columns = ['gene_id', '{}_fc'.format(cell_line), '{}_pval'.format(cell_line)]
        df = ORIGINAL_DF[columns]
        p_values = request.form['p_values']

        # transforming to highcharts format
        df.columns = ['name', 'y', 'p_value']
        df.y.astype(float)
        df.p_value.astype(float)
        df = df.round(decimals=3)
        if p_values == 'display':
            plot_series = list(df.T.to_dict().values())

        if p_values == 'drop':
            # replace 0 with nans and drop nan from p_val columns
            df = df.replace(0, pd.np.nan).dropna(axis=0, how="any", subset=['p_value'])
            plot_series = list(df.T.to_dict().values())

        if p_values == 'highlight':
            zero_df = df.loc[df['y'] == 0]
            zero_df['name'] = pd.Series(cell_line)
            non_zero_df = df.loc[df['y'] != 0]
            non_zero_df['name'] = pd.Series('{}_with_zero_p_values'.format(cell_line))
            plot_series = list(non_zero_df.T.to_dict().values()) + list(zero_df.T.to_dict().values())

        return render_template('main.html', cell_lines=CELL_LINES, genes=GENES, plot_series=plot_series,
                               selected_cell_line=cell_line, p_values=p_values)


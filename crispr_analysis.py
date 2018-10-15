import os

from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')

@app.route('/')
def show_scatter_plot(methods=['GET', 'POST']):
    final_table = 'FinalTableM2.txt'
    df = pd.read_csv(os.path.join(APP_STATIC, final_table), sep='\t')
    df = df.dropna()
    cell_lines = {}

    columns_to_select = []
    # cell_lines = []
    # {'name': 'AM2ML1', 'y': 0.3333}
    selecte_cell_lines = []
    genes = df['gene_id'].tolist()

    # excluding gene_id column
    for column in sorted(df.columns[1:]):
        if '_fc' in column:
            cell_line = column.split('_fc')[0]
            columns_to_select.append(column)
            # cell_lines.append(cell_line)
        # elif '_pval' in column:
        #     cell_line = column.split('_pval')[0]
        #     columns_to_select.append(column)
        # else:
        #     continue
        # # each row = gene
        for index, row in df.iterrows():
            value = row[column]
            if cell_line not in cell_lines:
                cell_lines[cell_line] = []
            try:
                float_value = float(value)
            except:
                float_value = -1
            cell_lines[cell_line].append(float_value)
    df = df[columns_to_select]
    plot_series = df.values.tolist()
    return render_template('main.html', cell_lines=cell_lines, plot_series=plot_series, genes=genes)


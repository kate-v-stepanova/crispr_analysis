import pandas as pd
from flask import Blueprint, render_template, request

import_page = Blueprint('data_import', __name__)


@import_page.route('/data_import', methods=['GET', 'POST'])
def import_data():
    from crispr_analysis import get_db
    rdb = get_db()
    if request.method == 'POST':
        data_type = request.form.get('data_type')
        input_file = request.files.get('input_file')
        # content = input_file.read()
        with_drugs = request.form.get('with_drugs')
        if data_type == "fold_changes":
            if with_drugs == 'without_drugs':
                df = pd.read_csv(input_file, sep='\t')
                header = list(df.columns)
                genes = df['gene_id'].tolist()
                cell_lines = []

                for column in header[1:]:
                    if '_fc' in column:
                        cell_line = column.split('_fc')[0]
                        if cell_line not in cell_lines:
                            cell_lines.append(cell_line)  # todo: unicode

                rdb.sadd('cell_lines', *set(cell_lines))
                rdb.sadd('genes', *set(genes))

                for cell_line in cell_lines:
                    inc_ess = 'increasedEssential_{}'.format(cell_line)
                    if 'increasedEssential_{}'.format(cell_line) not in df.columns:
                        df[inc_ess] = None
                    columns_to_select = ['gene_id', '{}_fc'.format(cell_line), '{}_pval'.format(cell_line), inc_ess]
                    # select only the columns for that cell line
                    current_df = df[columns_to_select]
                    # rename the columns
                    columns_to_rename = ['gene_id', 'fc', 'pval', 'inc_ess']
                    current_df.columns = columns_to_rename
                    rdb.set(cell_line, current_df[columns_to_rename].to_msgpack(encoding='utf-8'))
            elif with_drugs == "with_drugs":
                # file = "M2_fc_pval_all_screens_gathered.txt"
                df = pd.read_csv(input_file, sep='\t')
                cell_lines = df['cell_line'].unique()
                treatments = df['treatment'].unique()
                timepoints = df['time_point'].unique()
                cell_line_keys = []
                for cell_line in cell_lines:
                    cell_line_df = df.loc[df['cell_line'] == cell_line]
                    for treatment in treatments:
                        treatment_df = cell_line_df.loc[cell_line_df['treatment'] == treatment]
                        for timepoint in timepoints:
                            timepoint_df = treatment_df.loc[treatment_df['time_point'] == timepoint]
                            key = "{}_{}_{}".format(cell_line, treatment, timepoint)
                            cell_line_keys.append(key)
                            timepoint_df['inc_ess'] = pd.Series('n/a', index=timepoint_df.index)
                            timepoint_df = timepoint_df[['gene_id', 'fc', 'pval', 'treatment', 'inc_ess']]
                            rdb.set(key, timepoint_df.to_msgpack(encoding='utf-8'))

                rdb.sadd('treatments', *set(treatments))
                rdb.sadd('timepoints', *set(timepoints))
                rdb.sadd('cell_lines', *set(cell_line_keys))

        elif data_type == "norm_counts":
            if with_drugs == 'without_drugs':
                full_df = pd.read_csv(input_file, sep='\t')
                genes = full_df['gene_id'].unique()
                last_part = False
                for i in range(len(genes)):
                    gene = genes[i]
                    gene_df = full_df.loc[full_df['gene_id'] == gene]
                    gene_df = gene_df[['gene_id', 'cell_line', 'treatment', 'norm_counts']]
                    if i % 100 == 0 or (i + 100 >= len(genes) and last_part == False):
                        print('writing {} to {} out of {} genes'.format(i, min(i + 100, len(genes)), len(genes)))
                        last_part = True
                    key = '{}_counts'.format(gene)
                    rdb.set(key, gene_df.to_msgpack())
        elif data_type == "flush_db":
            rdb.flushall()
    return render_template('data_import.html')

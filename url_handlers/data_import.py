import pandas as pd
from flask import Blueprint, render_template, request

import_page = Blueprint('data_import', __name__)


@import_page.route('/data_import', methods=['GET', 'POST'])
def import_data():
    from crispr_analysis import get_db
    rdb = get_db()

    if request.method == 'POST':
        data_type = request.form.get('data_type')
        with_drugs = request.form.get('with_drugs')
        input_file = request.files.get('input_file')
        if data_type != 'flush_db' and input_file is None:
            return render_template('data_import.html', selected_data_type=data_type, with_drugs=with_drugs, error="Please select file!")
        email = request.form.get('email')
        notify = request.form.get('notify') == 'true'
        try:
            if data_type == "fold_changes":
                # doesn't matter with or without
                # if with_drugs == 'without_drugs':
                df = pd.read_csv(input_file, sep='\t')
                header = list(df.columns)
                genes = df['gene_id'].tolist()
                cell_lines = []

                for column in header:
                    if '_fc' in column:
                        cell_line = column.split('_fc')[0]
                        if cell_line not in cell_lines:
                            cell_lines.append(cell_line)  # todo: unicode

                for cell_line in cell_lines:
                    inc_ess = 'increasedEssential_{}'.format(cell_line)
                    if 'increasedEssential_{}'.format(cell_line) not in df.columns:
                        df[inc_ess] = 'n/a'
                    columns_to_select = ['gene_id', '{}_fc'.format(cell_line), '{}_pval'.format(cell_line), inc_ess]
                    # select only the columns for that cell line
                    current_df = df[columns_to_select]
                    # rename the columns
                    columns_to_rename = ['gene_id', 'fc', 'pval', 'inc_ess']
                    current_df.columns = columns_to_rename
                    rdb.set(cell_line, current_df[columns_to_rename].to_msgpack(encoding='utf-8'))

                rdb.sadd('cell_lines', *set(cell_lines))
                rdb.sadd('genes', *set(genes))
                success = "Data successfully imported. \nFile:{} \nCell lines: {} \nGenes:{}".format(
                    input_file.filename, len(cell_lines), len(genes))
                if notify and email:
                    send_email(email, message=success)
                return render_template('data_import.html', success=success)

            elif data_type == "norm_counts":
                if with_drugs == 'without_drugs':
                    full_df = pd.read_csv(input_file, sep='\t')

                    error = ''
                    required = ['cell_line', 'sample', 'gene_id', 'day', 'norm_counts']
                    if not set(required).issubset(set(full_df.columns)):
                        error = 'ERROR: incorrect header! \n'
                        error += 'Required columns: {}\n'.format(', '.join(required))
                        error += "Given: {}\n".format(', '.join(full_df.columns))
                    if error:
                        error += 'Filename: {}\n'.format(input_file.filename)
                        error += "Please read the instructions once again!!"
                        return render_template('data_import.html',
                           selected_data_type=data_type,
                           with_drugs=with_drugs,
                            error=error,
                        )
                    genes = full_df['gene_id'].unique()
                    cell_lines = full_df['cell_line'].unique()
                    last_part = False
                    for i in range(len(genes)):
                        gene = genes[i]
                        gene_df = full_df.loc[full_df['gene_id'] == gene]
                        gene_df = gene_df[['gene_id', 'cell_line', 'treatment', 'norm_counts']]

                        if i + 100 < len(genes) and i%100 == 0:
                            if notify and email:
                                message = 'writing {} to {} out of {} genes'.format(i, i+100, len(genes))
                                send_email(email, message=message)
                        elif i + 100 >= len(genes) and not last_part:
                            if notify and email:
                                send_email(email, 'writing {} to {} out of {} genes'.format(i, len(genes), len(genes)))
                            last_part = True

                        key = '{}_counts'.format(gene)
                        rdb.set(key, gene_df.to_msgpack())

                    success = "Data successfully imported. \nFile: {}\nCell lines: {} \nGenes:{}".format(
                        input_file.filename, len(cell_lines), len(genes))
                    if notify and email:
                        send_email(email,message=success)
                    return render_template('data_import.html', success=success)
                elif with_drugs == 'with_drugs':
                    full_df = pd.read_csv(input_file, sep='\t')

                    error = ''
                    required = ['cell_line', 'sample', 'gene_id', 'day', 'norm_counts']
                    if not set(required).issubset(set(full_df.columns)):
                        error = 'ERROR: incorrect header! \n'
                        error += 'Required columns: {}\n'.format(', '.join(required))
                        error += "Given: {}\n".format(', '.join(full_df.columns))
                    if error:
                        error += 'Filename: {}\n'.format(input_file.filename)
                        error += "Please read the instructions once again!!"
                        return render_template('data_import.html',
                           selected_data_type=data_type,
                           with_drugs=with_drugs,
                            error=error,
                        )
                    last_printed = False # for print message
                    cell_lines = full_df['cell_line'].unique()
                    genes = full_df['gene_id'].unique()
                    drugs = full_df['sample'].unique()  # this is only for day 21

                    for i in range(len(genes)):
                        gene=genes[i]
                        msg_pack = rdb.get('{}_counts'.format(gene))
                        if msg_pack is None:
                            # print('DID YOU IMPORT norm_counts WITHOUT DRUGS???')
                            error="Can't import {}. Did you import Normalized Counts WITHOUT drugs?\nCould not find gene {}".format(
                                input_file.filename, genes[i])
                            if notify and email:
                                send_email(email, message=error)
                            return render_template('data_import.html', error=error)
                        existing_df = pd.read_msgpack(msg_pack)
                        for cell_line in cell_lines:
                            # for all drugs we need day0, day7 and day21
                            day0_df = full_df.loc[(full_df['cell_line'] == cell_line) & (full_df['day'] == 0) & (full_df['gene_id'] == gene)]
                            day7_df = full_df.loc[(full_df['cell_line'] == cell_line) & (full_df['day'] == 7) & (full_df['gene_id'] == gene)]
                            for drug in drugs:
                                day21_df = full_df.loc[(full_df['cell_line'] == cell_line) & (full_df['sample'] == drug) & (full_df['day'] == 21) & (full_df['gene_id'] == gene)]
                                # this will be empty in case if sample = 'before1' or 'before2'
                                if day21_df.empty:
                                    # print("EMPTY: ", cell_line, drug, gene)
                                    continue

                                # day0vs7
                                # before
                                day0vs7_df = day0_df.copy()
                                day0vs7_df = day0vs7_df[['gene_id', 'cell_line', 'sample', 'norm_counts']]
                                day0vs7_df.columns = ['gene_id', 'cell_line', 'treatment', 'norm_counts']
                                day0vs7_df['cell_line'] = '{}_{}_day0vs7'.format(cell_line, drug)
                                day0vs7_df['treatment'] = 0
                                existing_df = existing_df.append(day0vs7_df.copy(), ignore_index=True)
                                # after
                                day0vs7_df = day7_df.copy()
                                day0vs7_df = day0vs7_df[['gene_id', 'cell_line', 'sample', 'norm_counts']]
                                day0vs7_df.columns = ['gene_id', 'cell_line', 'treatment', 'norm_counts']
                                day0vs7_df['cell_line'] = '{}_{}_day0vs7'.format(cell_line, drug)
                                day0vs7_df['treatment'] = 1
                                existing_df = existing_df.append(day0vs7_df.copy(), ignore_index=True)

                                # day7vs21
                                # before
                                day7vs21_df = day0vs7_df.copy()
                                day7vs21_df['cell_line'] = '{}_{}_day7vs21'.format(cell_line, drug)
                                day7vs21_df['treatment'] = 0
                                existing_df = existing_df.append(day7vs21_df.copy(), ignore_index=True)
                                # after
                                day7vs21_df = day21_df.copy()
                                day7vs21_df = day7vs21_df[['gene_id', 'cell_line', 'sample', 'norm_counts']]
                                day7vs21_df.columns = ['gene_id', 'cell_line', 'treatment', 'norm_counts']
                                day7vs21_df['cell_line'] = '{}_{}_day7vs21'.format(cell_line, drug)
                                day7vs21_df['treatment'] = 1
                                existing_df = existing_df.append(day7vs21_df.copy(), ignore_index=True)

                                # day0vs21
                                # before
                                day0vs21_df = day0vs7_df.copy()
                                day0vs21_df['cell_line'] = '{}_{}_day0vs21'.format(cell_line, drug)
                                day0vs21_df['treatment'] = 0
                                existing_df = existing_df.append(day0vs21_df.copy(), ignore_index=True)
                                # after
                                day0vs21_df = day7vs21_df.copy()
                                day0vs21_df['cell_line'] = '{}_{}_day0vs21'.format(cell_line, drug)
                                day0vs21_df['treatment'] = 1
                                existing_df = existing_df.append(day0vs21_df.copy(), ignore_index=True)

                        if i + 100 < len(genes) and i%100 == 0:
                            if notify and email:
                                message = 'writing {} to {} out of {} genes'.format(i, i+100, len(genes))
                                send_email(email, message=message)
                        elif i + 100 >= len(genes) and not last_printed:
                            if notify and email:
                                send_email(email, 'writing {} to {} out of {} genes'.format(i, len(genes), len(genes)))
                            last_printed = True
                    key = '{}_counts'.format(gene)
                    rdb.set(key, existing_df.to_msgpack())
                    success = "Data succesfully imported.\nFile: {} \nCell lines: {}\nGenes: {}".format(
                        input_file.filename, str(cell_lines), len(genes))
                    if notify and email:
                        send_email(email, success)
                    return render_template('data_import.html',
                                           selected_data_type=data_type,
                                           with_drugs=with_drugs,
                                           success=success,
                    )

            elif data_type == "flush_db":
                rdb.flushall()
                if notify and email:
                    send_email(email, 'Database succesfully flushed')
                return render_template('data_import.html', success='Database successfully flushed')
        except Exception as e:
            import traceback
            if notify and email:
                send_email(email, traceback.format_exc())
            return render_template('data_import.html', error='Import failed, error:\n {}'.format(traceback.format_exc()))
    return render_template('data_import.html')

@import_page.route('/download/<filename>', methods=['POST'])
def download_file(filename):
    filename = 'static/data_examples/{}.csv'.format(filename)
    df = pd.read_csv(filename, sep='\t')
    return df.to_csv(sep='\t', index=False)


def send_email(email, message):
    import smtplib
    import datetime
    email_from = 'crispr_analysis@yahoo.com'
    email_to = email
    subj = 'Data import in CRISPR_analysis'
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message_text = message

    msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" % (email_from, email_to, subj, date, message_text)

    username = email_from
    # dont tell anyone
    password = 'mlh1msh6'
    # try:
    server = smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465)
    server.connect("smtp.mail.yahoo.com", 465)
    server.login(username, password)
    server.sendmail(email_from, email_to, msg)
    server.quit()
    # except:
    #     import traceback
    #     traceback.format_exc()

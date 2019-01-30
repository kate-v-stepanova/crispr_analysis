import click
import redis
import pandas as pd

@click.group()
def cli():
    # do nothing
    pass


@cli.command()
@click.argument('input_file')
def init(input_file):
    # default host: 127.0.0.1, default port: 6379.
    # to change, use redis.StrictRedis(host=HOST, port=PORT)
    # but we are not going to change this
    rdb = redis.StrictRedis()

    df = pd.read_csv(input_file, sep='\t')
    header = list(df.columns)
    genes = df['gene_id'].tolist()
    cell_lines = []

    for column in header[1:]:
        if '_fc' in column:
            cell_line = column.split('_fc')[0]
            if cell_line not in cell_lines:
                cell_lines.append(cell_line) # todo: unicode

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

@cli.command()
@click.argument('input_file')
def counts(input_file):
    rdb = redis.StrictRedis()
    full_df = pd.read_csv(input_file, sep='\t')
    genes = full_df['gene_id'].unique()
    for i in range(len(genes)):
        gene = genes[i]
        gene_df = full_df.loc[full_df['gene_id'] == gene]
        gene_df = gene_df[['gene_id', 'cell_line', 'treatment',  'norm_counts']]
        if i%100 == 0 or i + 100 >= len(genes):
            print('writing {} to {} out of {} genes'.format(i, min(i+100, len(genes)), len(genes)))
        key = '{}_counts'.format(gene)
        rdb.set(key, gene_df.to_msgpack())


@cli.command()
@click.argument('input_file')
# @click.option('--drugs/--no-drugs', default=False)
@click.argument('cell_line', required=False)
def counts_with_drugs(input_file, cell_line):
    print(cell_line)
    rdb = redis.StrictRedis()
    import_df = pd.read_csv(input_file, sep='\t')
    genes = import_df['gene_id'].unique()
    for i in range(len(genes)):
        gene = genes[i]
        existing_df = pd.read_msgpack(rdb.get('{}_counts'.format(gene)))
        # columns_of_df = ['gene_id', 'cell_line', 'treatment', 'norm_counts']
        gene_df = import_df.loc[import_df['gene_id'] == gene]
        # ['sample_id', 'treatment', 'replicate', 'guide_id', 'counts', 'gene_id', 'seq', 'library', 'norm_counts']
        samples = gene_df['sample_id'].unique()
        week0_df = pd.DataFrame(columns=['gene_id', 'cell_line', 'treatment', 'norm_counts'])
        week1_df = pd.DataFrame(columns=['gene_id', 'cell_line', 'treatment', 'norm_counts'])
        for sample_id in samples:
            gene_df = import_df.loc[(import_df['sample_id'] == sample_id) & (import_df['gene_id'] == gene)]
            if sample_id == 'day0':
                gene_df = gene_df[['gene_id', 'treatment', 'norm_counts']]
                gene_df['treatment'] = 0
                # mock drug
                gene_df['cell_line'] = '{}_mock_week0'.format(cell_line)
                week0_df.append(gene_df, ignore_index=True)
                # cisplatin drug
                gene_df = gene_df.copy()
                gene_df['cell_line'] = '{}_cis_week0'.format(cell_line)
                week0_df.append(gene_df, ignore_index=True)
                # topotecan drug
                gene_df = gene_df.copy()
                gene_df['cell_line'] = '{}_topo_week0'.format(cell_line)
                week0_df.append(gene_df, ignore_index=True)
                # irradiation drug
                gene_df = gene_df.copy()
                gene_df['cell_line'] = '{}_irr_week0'.format(cell_line)
                week0_df.append(gene_df, ignore_index=True)
                # fu drug
                gene_df = gene_df.copy()
                gene_df['cell_line'] = '{}_fu_week0'.format(cell_line)
                week0_df.append(gene_df, ignore_index=True)
            elif sample_id == 'day7':
                gene_df = gene_df[['gene_id', 'treatment', 'norm_counts']]
                gene_df['treatment'] = 1
                # mock drug
                gene_df['cell_line'] = '{}_mock_week0'.format(cell_line)
                week0_df.append(gene_df, ignore_index=True)
                # cisplatin drug
                gene_df = gene_df.copy()
                gene_df['cell_line'] = '{}_cis_week0'.format(cell_line)
                week0_df.append(gene_df, ignore_index=True)
                # topotecan drug
                gene_df = gene_df.copy()
                gene_df['cell_line'] = '{}_topo_week0'.format(cell_line)
                week0_df.append(gene_df, ignore_index=True)
                # irradiation drug
                gene_df = gene_df.copy()
                gene_df['cell_line'] = '{}_irr_week0'.format(cell_line)
                week0_df.append(gene_df, ignore_index=True)
                # fu drug
                gene_df = gene_df.copy()
                gene_df['cell_line'] = '{}_fu_week0'.format(cell_line)
                week0_df.append(gene_df, ignore_index=True)
                ## the same for week1
                gene_df = gene_df.copy()
                gene_df['treatment'] = 0
                # mock drug
                gene_df['cell_line'] = '{}_mock_week1'.format(cell_line)
                week1_df.append(gene_df, ignore_index=True)
                # cisplatin drug
                gene_df = gene_df.copy()
                gene_df['cell_line'] = '{}_cis_week1'.format(cell_line)
                week1_df.append(gene_df, ignore_index=True)
                # topotecan drug
                gene_df = gene_df.copy()
                gene_df['cell_line'] = '{}_topo_week1'.format(cell_line)
                week1_df.append(gene_df, ignore_index=True)
                # irradiation drug
                gene_df = gene_df.copy()
                gene_df['cell_line'] = '{}_irr_week1'.format(cell_line)
                week1_df.append(gene_df, ignore_index=True)
                # fu drug
                gene_df = gene_df.copy()
                gene_df['cell_line'] = '{}_fu_week1'.format(cell_line)
                week1_df.append(gene_df, ignore_index=True)
            elif sample_id == 'day21mock':
                gene_df = gene_df.copy()
                gene_df['treatment'] = 1
                gene_df['cell_line'] = '{}_mock_week1'.format(cell_line)
                week1_df.append(gene_df, ignore_index=True)
            elif sample_id == 'day21cis':
                gene_df = gene_df.copy()
                gene_df['treatment'] = 1
                gene_df['cell_line'] = '{}_cis_week1'.format(cell_line)
                week1_df.append(gene_df, ignore_index=True)
            elif sample_id == 'day21irr':
                gene_df = gene_df.copy()
                gene_df['treatment'] = 1
                gene_df['cell_line'] = '{}_irr_week1'.format(cell_line)
                week1_df.append(gene_df, ignore_index=True)
            elif sample_id == 'day21topo':
                gene_df = gene_df.copy()
                gene_df['treatment'] = 1
                gene_df['cell_line'] = '{}_topo_week1'.format(cell_line)
                week1_df.append(gene_df, ignore_index=True)
            elif sample_id == 'day21fu':
                gene_df = gene_df.copy()
                gene_df['treatment'] = 1
                gene_df['cell_line'] = '{}_fu_week1'.format(cell_line)
                week1_df.append(gene_df, ignore_index=True)

        existing_df.append(week0_df, ignore_index=True)
        existing_df.append(week1_df, ignore_index=True)
        if i%100 == 0 or i + 100 >= len(genes):
            print('writing {} to {} out of {} genes'.format(i, min(i+100, len(genes)), len(genes)))
        key = '{}_counts'.format(gene)
        rdb.set(key, existing_df.to_msgpack())

@cli.command()
def flush():
    rdb = redis.StrictRedis()
    rdb.flushall()

@cli.command()
@click.argument('input_file')
def with_drugs(input_file):
    rdb = redis.StrictRedis()
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


if __name__ == '__main__':
    cli()

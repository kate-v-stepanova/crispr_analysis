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
        if (i%100 == 0 or i + 100 >= len(genes)):
            print('writing {} to {} out of {} genes'.format(i, min(i+100, len(genes)), len(genes)))
        key = '{}_counts'.format(gene)
        rdb.set(key, gene_df.to_msgpack())


@cli.command()
def flush():
    rdb = redis.StrictRedis()
    rdb.flushall()

if __name__ == '__main__':
    cli()

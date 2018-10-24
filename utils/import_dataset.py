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

    for column in header:
        if '_fc' in column:
            cell_line = column.split('_fc')[0]
            if cell_line not in cell_lines:
                cell_lines.append(cell_line)

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
def flush():
    rdb = redis.StrictRedis()
    rdb.flushall()

if __name__ == '__main__':
    cli()

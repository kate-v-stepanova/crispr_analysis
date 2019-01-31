import pandas as pd
from flask import Blueprint, render_template, request
# import sklearn

from sklearn.cluster import KMeans

cluster_page = Blueprint('clustering', __name__)


@cluster_page.route('/clustering', methods=['GET', 'POST'])
def cluster_data():
    from crispr_analysis import get_db
    rdb = get_db()

    cell_lines = rdb.smembers('cell_lines')
    cell_lines = [cell_line.decode('utf-8') for cell_line in cell_lines]
    if request.method == 'POST':
        selected_cell_lines = request.form.getlist('cell_lines')
        clustering_method = request.form.get('clustering_method')
        selected_filter = request.form.get('filter_data')
        selected_genes = request.form.get('selected_genes').strip().split()
        number_of_clusters = request.form.get('number_of_clusters')
        if number_of_clusters:
            # i don't make any checks, because the form on submit already makes sure that entered number is int
            number_of_clusters = int(number_of_clusters)

        # thresholds
        wt_fc_max = float(request.form.get('wt_fc_max'))
        wt_fc_min = float(request.form.get('wt_fc_min'))
        wt_pval = float(request.form.get('wt_pval_max'))
        fc_max = float(request.form.get('fc_max'))
        fc_min = float(request.form.get('fc_min'))
        pval = float(request.form.get('pval_max'))

        full_df = None
        wt_df = None
        if selected_filter == 'by_thresholds':
            selected_genes = []
            for cell_line in selected_cell_lines:
                data = rdb.get(cell_line)
                if not data:
                    continue
                df = pd.read_msgpack(data)

                df = df[['gene_id', 'fc', 'pval']]
                df.columns = ['gene_id', '{}_fc'.format(cell_line), '{}_pval'.format(cell_line)]
                full_df = df.copy() if full_df is None else pd.merge(full_df, df, how='outer', on='gene_id')

                # Filter by thresholds
                if 'WT' in cell_line:
                    df = df.loc[df['{}_fc'.format(cell_line)] >= wt_fc_min]
                    df = df.loc[df['{}_fc'.format(cell_line)] <= wt_fc_max]
                    df = df.loc[df['{}_pval'.format(cell_line)] <= wt_pval]
                else:
                    df = df.loc[df['{}_fc'.format(cell_line)] >= fc_min]
                    df = df.loc[df['{}_fc'.format(cell_line)] <= fc_max]
                    df = df.loc[df['{}_pval'.format(cell_line)] <= pval]

                if 'WT' in cell_line:
                    wt_df = df.copy()

                selected_genes += list(df['gene_id'].unique())
            #     selected_genes += list(df['gene_id'].unique())
            selected_genes = list(set(selected_genes))
            # df = full_df.loc[full_df['gene_id'].isin(selected_genes)].reset_index()
        else:
            for cell_line in selected_cell_lines:
                data = rdb.get(cell_line)
                if not data: continue
                df = pd.read_msgpack(data)
                df = df[['gene_id', 'fc', 'pval']]
                df.columns = ['gene_id', '{}_fc'.format(cell_line), '{}_pval'.format(cell_line)]
                if 'WT' in cell_line:
                    wt_df = df.copy()
                else:
                    full_df = df.copy() if full_df is None else pd.merge(full_df, df, how='outer', on='gene_id')

        if wt_df is not None:
            full_df = pd.merge(full_df, wt_df, how='inner', on='gene_id')

        if selected_filter == 'do_not_filter':
            df = full_df.copy()
        elif selected_filter == 'by_thresholds':
            df = full_df.loc[full_df['gene_id'].isin(selected_genes)].reset_index()
            df = pd.merge(df, wt_df, how='inner', on='gene_id')
        else:
            df = full_df.loc[full_df['gene_id'].isin(selected_genes)].reset_index()

        # clustering
        df = df.drop_duplicates()

        df_to_cluster = df.drop(columns=['gene_id']).round(decimals=3)
        kmeans = KMeans(n_clusters=number_of_clusters, random_state=0).fit(df_to_cluster)
        labels = kmeans.labels_
        df_to_cluster['cluster'] = labels
        df_to_cluster['gene_id'] = df['gene_id']

        plot_series = []
        shapes = ["circle", "square", "diamond", "triangle", "triangle-down"]
        colors = ['#b3e6ff', '#ffe6b3', '#ccffb3', '#ffb3b3', '#d699ff', 'black', 'grey']
        df_to_cluster = df_to_cluster.sort_values(by=['cluster'])

        ordered_genes = []
        for cell_line in selected_cell_lines:
            df1 = df_to_cluster[['gene_id', '{}_fc'.format(cell_line), '{}_pval'.format(cell_line), 'cluster']].copy()
            plot_data = []
            for i in range(number_of_clusters):
                df = df1.loc[df_to_cluster['cluster'] == i]
                df.columns = ['gene_id', 'fc', 'pval', 'cluster']
                df['y'] = df['fc']
                df['name'] = df['gene_id']
                df['cell_line'] = cell_line
                df['color'] = colors[i % len(colors)]
                df['cluster_size'] = len(df)
                plot_data += list(df.T.to_dict().values())
                ordered_genes += df['gene_id'].tolist()
            plot_series.append({
                # 'name': 'Cluster {}'.format(i),
                'turboThreshold': len(df_to_cluster),
                'data': plot_data,
                'marker': {
                    'symbol': shapes[selected_cell_lines.index(cell_line) % len(selected_cell_lines)]
                }
            })

        df_to_cluster.insert(0, '#', range(1, len(df_to_cluster)+1))
        columns = []
        for cell_line in selected_cell_lines:
            columns += ['{}_fc'.format(cell_line), '{}_pval'.format(cell_line)]
        df_to_cluster = df_to_cluster[['#', 'gene_id', 'cluster'] + columns]
        data_table = {
            'header': df_to_cluster.columns,
            'rows': df_to_cluster.values.tolist(),
            'csv': df_to_cluster.to_csv(sep='\t', index=False)
        }

        selected_genes = ordered_genes
        filtered_genes = None
        if selected_filter == 'by_thresholds':
            filtered_genes = selected_genes
            selected_genes = None

        return render_template('clustering.html',
                               cell_lines=cell_lines,
                               selected_cell_lines=selected_cell_lines,
                               selected_filter=selected_filter,
                               clustering_method=clustering_method,
                               selected_thresholds={
                                   'wt_fc_max': wt_fc_max,
                                   'wt_fc_min': wt_fc_min,
                                   'wt_pval': wt_pval,
                                   'fc_max': fc_max,
                                   'fc_min': fc_min,
                                   'pval': pval
                               },
                               selected_genes=selected_genes,
                               filtered_genes=filtered_genes,
                               plot_series=plot_series,
                               number_of_clusters=number_of_clusters,
                               data_table=data_table)

    return render_template('clustering.html', cell_lines=cell_lines, selected_filter="do_not_filter")


# js post request - called on selected an entity from a list
@cluster_page.route('/get_norm_counts/<gene>/<cell_lines>', methods=['POST'])
def get_norm_counts(gene, cell_lines):
    # this import has to be here!!
    from crispr_analysis import get_db
    rdb = get_db()
    cell_lines = cell_lines.split(',')
    msgpack = rdb.get('{}_counts'.format(gene))
    if msgpack is None:
        return jsonify({
            'data': [],
            'errors': ['No counts for gene {} found'.format(gene)]
        })
    gene_df = pd.read_msgpack(msgpack)
    series_before = []
    series_after = []
    outliers = []
    error_messages = []
    for i in range(len(cell_lines)):
        cell_line = cell_lines[i]
        # key = 'RPE_{}'.format(cell_line)
        df = gene_df.loc[gene_df['cell_line'] == cell_line]
        # if df.empty:
        #     key = cell_line
        #     df = gene_df.loc[gene_df['cell_line'] == key]
        if df.empty:
            error_messages.append('No counts for gene: {} and cell line: {}. '.format(gene, cell_line))
            continue

        # keep only the ones that are within +3 to -3 standard deviations
        without_outliers = df[np.abs(df.norm_counts - df.norm_counts.mean()) <= (3 * df.norm_counts.std())]
        only_outliers = df[np.abs(df.norm_counts - df.norm_counts.mean()) > (3 * df.norm_counts.std())]
        before = without_outliers.loc[without_outliers['treatment'] == 0]
        after = without_outliers.loc[without_outliers['treatment'] == 1]

        # calculate boxplot data
        q1, median, q3 = before.norm_counts.quantile([0.25, 0.5, 0.75]).round(decimals=3).tolist()
        series_before.append([
            before['norm_counts'].min().round(decimals=3),
            q1,
            median,
            q3,
            before['norm_counts'].max().round(decimals=3)])
        q1, median, q3 = after.norm_counts.quantile([0.25, 0.5, 0.75]).round(decimals=3).tolist()
        series_after.append([
                after['norm_counts'].min().round(decimals=3),
                q1,
                median,
                q3,
                after['norm_counts'].max().round(decimals=3)])
        for index, row in only_outliers.iterrows():
            x = i
            y = round(row['norm_counts'], 3)
            treatment = 'Before Treatment' if int(row['treatment']) == 0 else 'After Treatment'
            outliers.append({
                'x': x,
                'y': y,
                'treatment': treatment,
                'cell_line': cell_line,
                'color': 'black' if treatment == 'After Treatment' else '#7cb5ec'
            })

    counts_series = [{
            'name': 'Before Treatment',
            'data': series_before,
            'color': '#7cb5ec',
        }, {
            'name': 'After Treatment',
            'data': series_after,
            'color': 'black',
        }, {'name': 'Outliers',
            'type': 'scatter',
            'data': outliers,
            'color': 'black',
            'tooltip': {
                'pointFormat': '<br>cell line: {point.cell_line}<br>norm. counts: {point.y}<br>treatment: {point.treatment}',
            }
        }
    ]
    return jsonify({
        'data': counts_series,
        'errors': error_messages,
    })

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

        # thresholds
        wt_fc_max = float(request.form.get('wt_fc_max'))
        wt_fc_min = float(request.form.get('wt_fc_min'))
        wt_pval = float(request.form.get('wt_pval_max'))
        fc_max = float(request.form.get('fc_max'))
        fc_min = float(request.form.get('fc_min'))
        pval = float(request.form.get('pval_max'))

        wt_df = None
        joint_df = None
        for cell_line in selected_cell_lines:
            data = rdb.get(cell_line)
            if not data:
                continue
            df = pd.read_msgpack(data)
            df = df[['gene_id', 'fc', 'pval']]
            df.fc.astype(float)
            df.pval.astype(float)
            # Filter by genes
            if selected_filter == 'by_genes':
                df = df.loc[df['gene_id'].isin(selected_genes)].reset_index()
            # Filter by thresholds
            elif selected_filter == 'by_thresholds':
                if 'WT' in cell_line:
                    df = df.loc[df['fc'] >= wt_fc_min]
                    df = df.loc[df['fc'] <= wt_fc_max]
                    df = df.loc[df['pval'] <= wt_pval]
                else:
                    df = df.loc[df['fc'] >= fc_min]
                    df = df.loc[df['fc'] <= fc_max]
                    df = df.loc[df['pval'] <= pval]
            df.columns = ['gene_id', '{}_fc'.format(cell_line), '{}_pval'.format(cell_line)]
            if cell_line == 'WT':
                wt_df = df
            else:
                joint_df = df.copy() if joint_df is None else pd.merge(joint_df, df, how='outer', on='gene_id')

        if wt_df is not None:
            joint_df = pd.merge(joint_df, wt_df, how='inner', on='gene_id')

        columns = list(joint_df.columns)
        df_to_cluster = joint_df.drop(columns=['gene_id'])
        df_to_cluster = df_to_cluster.dropna()
        # Using sklearn
        km = KMeans(n_clusters=3)
        km.fit(df_to_cluster.values)
        # Get cluster assignment labels
        labels = km.labels_
        # Format results as a DataFrame
        results = pd.DataFrame([df_to_cluster.index, labels]).T

        results = pd.concat([results, joint_df], axis=1)
        # 1 is the name of the cluster column in results df
        results = results[columns + [1]]
        results.columns = columns + ['cluster']

        results = results.fillna('null')
        results['y'] = results['{}_fc'.format(selected_cell_lines[0])].copy()
        plot_series = []
        for i in range(5):
            df = results.loc[results['cluster'] == i]

            plot_series.append({
                'name': 'cluster_{}'.format(i),
                'data': list(df.T.to_dict().values()),
                'turboThreshold': len(df),
            })
        selected_genes = results['gene_id'].tolist()
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
                               plot_series=plot_series)

    return render_template('clustering.html', cell_lines=cell_lines, selected_filter="do_not_filter")

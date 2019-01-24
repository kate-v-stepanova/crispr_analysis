# crispr_analysis
## Installation
1. Clone repo to the filesystem
```
git clone git@github.com:kate-v-stepanova/crispr_analysis.git
```
2. Create a virtual environment (e.g. [conda](https://conda.io/docs/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands)) and install the requirements
```
conda create -n crispr_analysis python=3
source activate crispr_analysis
pip install -r crispr_analysis/utils/requirements.txt
```
3. Set up [redis](https://redis.io/topics/quickstart)
4. Export environmental variable 
```
export FLASK_APP=crispr_analysis/crispr_analysis.py
```
5. Run flask. Option `--host 0.0.0.0` means that the web-application will be available for other ips (not only for localhost)
```
flask run --host 0.0.0.0
```

install=$1
if [ $i = "-i" ]; then
    echo "installing conda and requirements.txt"
    conda create -n crispr_analysis
    source activate crispr_analysis
    pip install -r requirements.txt
fi
source activate crispr_analysis
export FLASK_APP=crispr_analysis.py
export FLASK_ENV=development
flask run
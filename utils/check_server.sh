export TZ=Europe/Berlin
now=$(date)
if pgrep -x "redis-server" > /dev/null
then
	echo $now ': Redis Running'
else
	echo $now: ': Redis Restarting'
	redis-server &
fi
if pgrep -x "flask" > /dev/null
then
    echo $now ': Flask Running'
else
	echo $now ": Restarting"
	source activate crispr_analysis
	export FLASK_APP='/home/stepanova/crispr_analysis/crispr_analysis.py'
	export FLASK_ENV=development
	flask run --host 0.0.0.0 &
fi

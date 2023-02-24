wc_port=${1}
if [[ -z ${wc_port} ]]
then
	wc_port=8000
fi
wc_env=${2}
. act_wordle_cheater.sh ${wc_env}
uvicorn wordle_server:app --reload --port ${wc_port}

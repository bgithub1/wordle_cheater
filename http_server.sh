# run the http server that allows you to access wordle_cheater's web app
# Example: run on default port of 3001
# . http_server.sh
# Example: run on  port of 3004
# . http_server.sh 3004
# . ~/cdpylr.sh
# cd wordle_cheater
port=${1}
if [[ -z ${port} ]]
then
	port=3001
fi
. act_wordle_helper.sh
python3 -m http.server ${port}

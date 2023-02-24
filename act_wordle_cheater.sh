# activate pip environment wordle_cheater
# Example: use default location
# . act_wordle_cheater.sh
# Example: use specific virtual env location
# . act_wordle_cheater.sh ~/Virtualenvs3/my_worldle_cheater_env
virtenv=${1}
if [[ -z ${virtenv} ]]
then
	virtenv=$(cd ~/Virtualenvs3/wordle_cheater;pwd)
else
	virtenv=$(cd ${virtenv};pwd)
fi
source  ${virtenv}/bin/activate

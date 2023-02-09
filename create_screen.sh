screen -S wordle_py_server -dm bash -c "bash uvicorn_run.sh"
sleep 5
screen -S wordle_http_server -dm bash -c "nvm use 16.13.1;bash http_server.sh"

echo launching http_server.sh
osascript -e 'tell app "Terminal"
  do script ". ~/cdpylr.sh;cd wordle_cheater;bash http_server.sh"
end tell'
sleep 1

echo launching 'uvicorn wordle_server:app --reload'
osascript -e 'tell app "Terminal"
  do script ". ~/cdpylr.sh;cd wordle_cheater;. act_wordle_helper.sh;uvicorn wordle_server:app --reload"
end tell'
sleep 1

echo launching pages_wordle
bash ~/open_pages.sh $(pwd)/pages_wordle.txt

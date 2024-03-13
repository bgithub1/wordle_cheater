## Wordle Cheater 
Use Wordle Helper to find possible words (e.g., *cheat*) while you're playing Wordle. 

For basic usage, see ```using_wordle_cheater.ipynb```.

To play directly, go to: https://billybyte.com/wordl

To launch the http server and fastapi python backend:
  1. In a separate bash terminal or bash screen, execute `bash http_server.sh`
  2. In a separate bash terminal or bash screen, execute `bash uvicorn_run.sh`
  3. Open a browser and put `http://localhost:3001` in the address bar.
___

### To run http_server.sh locally (like on your mac), you will will want the html file `index.html` to send requests to the locally running wordle_server.py that you ran by executing `bash uvicorn_run.sh`.  So, YOU MUST EDIT `index.html` to change the lines:

`    // WHEN TESTING LOCALLY, comment this line out`
`    var fetch_http = "https://billybyte.com/wordle_server";`
    
`    // WHEN TESTING LOCALLY, UNCOMMENT this line`
`    // var fetch_http = "http://localhost:8000";`

Comment out the `https://billybyte.com/wordle_server";` line, and uncomment the line `http://localhost_8000;` line

Remember to undo those change when pushing the code back to github, so that when you git fetch and get merge the code on the live server, the server uses `https://billybyte.com/wordle_server`, NOT `http://localhost:8000";` .


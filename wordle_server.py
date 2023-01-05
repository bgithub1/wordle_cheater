# import itertools
# import string
import numpy as np
# # import requests
# # from lxml import html
# import datetime

# import ipywidgets as widgets
# from IPython.display import display,display_html

# import tqdm
# import pdb
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import io

import wordle_cheater as wrdlc


app = FastAPI()

# code goes here
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://www.billybyte.com",
    "https://www.billybyte.com",
    "http://billybyte.com",
    "https://billybyte.com",
    "http://localhost",
    "http://localhost:3001",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
async def root():
    return {"message": "Welcome to wordle_server"}

@app.get("/wordl/solutions")
async def solutions():
    wdl = wrdlc.wordl()
    df = wdl.df_word_history.dropna()
    # df['number'] = df['number'].astype(str)
    return df.to_dict(orient="records")



@app.get("/wordl")
async def load_wordl(filters:str="slate,33333,minor,33223,goony,32123"):
    params = np.array(filters.split(',')).reshape(-1,2)
    wdl = wrdlc.wordl()
    for p in params:
        word = p[0]
        num_list = [int(v) for v in p[1]]
        wdl.add_word(word,num_list)        
    df = wrdlc.filter_words(wdl.try_it()) 
    df.probability = df.probability.round(5)
    print(filters)
    print(df)
    
    return df.to_dict(orient="records")       


 


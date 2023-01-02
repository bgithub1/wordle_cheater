import itertools
import string
import numpy as np
import requests
from lxml import html
import datetime
import pytz

import ipywidgets as widgets
from IPython.display import display,display_html

import tqdm
import pdb
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import io


USE_LOCAL_CSV=True
if USE_LOCAL_CSV:
    df = pd.read_csv('df_wordl_words.csv')
    df_ugf = pd.read_csv('unigram_freq.csv')
else:
    sheet_url ='https://docs.google.com/spreadsheets/d/1rYkOLXEaSvq5cMY1IfpwTx4RRtIv8GNg-CyoM0Ysc84/edit#gid=2066977162'
    csv_export_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    df = pd.read_csv(csv_export_url)
    sheet_url ='https://docs.google.com/spreadsheets/d/1NbUDdW_W4eTSuiRpcwnXB7B2r5JO4A3nbHfPxyIKXcY/edit#gid=1269657289'
    csv_export_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    df_ugf = pd.read_csv(csv_export_url)


def get_word_history():
    ret_val = None
    url_to_search = "https://screenrant.com/wordle-answers-updated-word-puzzle-guide/"
    xpath = "//a[contains(@href,'hints')]/.."
    # Make an HTTP request to the webpage
    response = requests.get(
        url_to_search, 
        headers={
            "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        }
    )

    # Parse the HTML content
    doc = html.fromstring(response.content)

    # Execute an XPath search on the document
    results = doc.xpath(xpath)
    if len(results)>0:
        ret_val = [
            v.text_content().split('-') 
            for v in results
        ]
        ret_val = [
            [rv[0].strip(),rv[1].strip(),rv[2].strip()] 
            for rv in ret_val if len(rv)==3
        ]
        ret_val = [
            [
                rv[0],
                int(rv[1][1:]),
                rv[2]
            ]
            for rv in ret_val
        ]
        df_word_hist = pd.DataFrame(ret_val,columns=['date','number','solution'])
        df_word_hist = df_word_hist.sort_values('number',ascending=False)
        df_word_hist.index = range(len(df_word_hist))
    return df_word_hist

# +
# nltk_words = df.word.values
df_ww = pd.read_csv('wordle_words.csv')
df_ww['word'] = df_ww.index
df_ww.index = range(len(df_ww))

df_ugf = df_ugf[~df_ugf.word.isna()]    
df_ugf.word = df_ugf.word.str.strip(' ')

df_ugf = df_ugf[df_ugf.word.isin(df_ww.word.values)]

c1 = df_ugf.word.str.len()==5
c2 = df_ugf.word.str.slice(0,1).str.lower() == df_ugf.word.str.slice(0,1)
nltk_words = df_ugf[c1 & c2].word.values


# -

def get_monthday():
    eastern = pytz.timezone("US/Eastern")
    now = datetime.datetime.now(tz=eastern)
    month = now.strftime('%b')
    day = str(int(now.strftime('%d')))
    monthday = month+" "+day
    return monthday

def new_condition(word,letter_status):
    good_letters = []
    for i,letter in enumerate(list(word)):
        if letter_status[i]<3:
            good_letters.append(letter)
    def inner_test(w):
        new_conditions = []
        for i,letter in enumerate(list(word)):
            if letter_status[i]==0:
                new_conditions.append(
                    letter in w 
                )                
            elif letter_status[i]==1:
                new_conditions.append(
                    letter in w[i] 
                )                
            elif letter_status[i]==2:
                new_conditions.append(
                    (letter in w) and (letter not in w[i])
                )
            else:
                new_conditions.append(
                    letter not in w
                )
        return new_conditions
    return inner_test,good_letters

class wordl():
    def __init__(self,show_progress=True):
        self.wordlist = []
        self.letter_list = []
        self.letter_status = []
        self.conditions = []
        self.show_progress = show_progress
        all_words = set(
            nltk_words
        )
        self.nltk_words =  set(
            [
                wo 
                for wo in all_words
                if (len(wo)==5) and (wo.lower()==wo)
            ]
        )

        # get wordle word history
        self.df_word_history = pd.read_csv('./temp_folder/df_word_history.csv')
        c1 = self.df_word_history['date']==get_monthday()
        if len(self.df_word_history[c1])!=1:
            self.df_word_history = get_word_history()
            self.df_word_history.to_csv('./temp_folder/df_word_history.csv',index=False)
                        
        self.todays_word = self.df_word_history.iloc[0].solution.lower()

    
    def add_word(self,word,letter_status,debug_word=''):
        self.wordlist.append(word)
        self.letter_status.append(letter_status)
        condition_list,letter_list = new_condition(word,letter_status)
        self.conditions.append(condition_list)
        self.letter_list.extend(letter_list)
        self.letter_list = list(set(self.letter_list))
    
    def conds(self,w):
        cond_results = []
        for i in range(len(self.conditions)):
            cond_results.extend(self.conditions[i](w))
        return all(cond_results)
    


    def try_it(self,letter_list=None):
        words = []
        curr_lets = self.letter_list if letter_list is None else letter_list
        poss_words = [
            w for w in self.nltk_words
            if len(set(curr_lets).intersection(w))==len(curr_lets)
        ]
        for w in poss_words:
            if self.conds(w):
                words.append(w)
        return words

def filter_words(words):
    df_new = df_ugf[df_ugf.word.isin(words)].sort_values('count',ascending=False).copy()
    count_sum = df_new['count'].sum()
    df_new['probability'] = df_new['count']/count_sum
    df_new.index = range(1,len(df_new)+1)
    return df_new


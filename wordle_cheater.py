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
import os
import pdb


USE_LOCAL_CSV = os.path.exists('df_wordl_words.csv') and os.path.exists('unigram_freq.csv')
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


def get_xpath_solution_value(v):
    d = v.text_content().strip().split('Wordle')
    d = d[1].split()[-1]
    return d.strip()

def get_xpath_solution_date(v):
    d = v.text_content().strip().split('Wordle')
    d = d[0].split()[-2:]
    d[0] = d[0][0:3]
    d = ' '.join(d)
    return d.strip()

def get_xpath_solution_number(v):
    r = str(v.text_content().strip().split()[-1])
    n = int(r.replace('#','').replace(')',''))
    return n

def get_word_history_2():
    ret_val = None
    url_to_search = "https://gamerant.com/todays-wordle-solution-every-answer-ny-times-archive/"
    xpath_solution_number = "//h2[contains(@id,'wordle-solution')]"
    xpath_solution = "//h2[contains(@id,'wordle-solution')]/following-sibling::section//p"
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
    solutions = doc.xpath(xpath_solution)
    solution_numbers = doc.xpath(xpath_solution_number)

    if len(solutions)>0:
        ret_val = [
            [
                get_xpath_solution_date(solutions[i]),
                get_xpath_solution_number(solution_numbers[i]),
                get_xpath_solution_value(solutions[i])
            ]
            for i in range(len(solutions))
        ]
        df_word_hist = pd.DataFrame(ret_val,columns=['date','number','solution'])
        df_word_hist = df_word_hist.sort_values('number',ascending=False)
        df_word_hist.index = range(len(df_word_hist))
    return df_word_hist

def fix_date(d):
    ds = d.strip().split(' ')
    try:
        m = ds[0][0:3]
        ds = f"{m} {ds[1]}"
    except:
        return d
    return ds

def get_word_history():
    ret_val = None
    url_to_search = "https://screenrant.com/wordle-answers-updated-word-puzzle-guide/"
    # xpath = "//a[contains(@href,'hints')]/.."
    xpath = "//ul/li//strong/.."

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
        ret_val = results[0:300]
        ret_val = [
            v.text_content().split('-') 
            for v in results
        ]
        ret_val = [
            [
                # rv[0].strip(),
                fix_date(rv[0]),
                rv[1].strip(),
                rv[2].strip()
            ] 
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
    return df_word_hist.iloc[0:300]

def get_combined_word_histories():
    df_word_hist = get_word_history()
    df_word_hist_2 = get_word_history_2()
    df_wh = pd.concat([df_word_hist_2,df_word_hist],ignore_index=True)
    df_wh = df_wh.drop_duplicates('date')
    df_wh = df_wh.sort_values('number',ascending=False)
    df_wh.index = range(len(df_wh))
    return df_wh

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

def get_today_monthday():
    eastern = pytz.timezone("US/Eastern")
    now = datetime.datetime.now(tz=eastern)
    month = now.strftime('%b')
    # day = str(int(now.strftime('%d')))
    day = now.strftime('%d')
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

        # # Get wordle word history
        # # First, init a blank DataFrame, in case you have never run get_word_history()
        # self.df_word_history = pd.DataFrame(
        #     {'date':[],'number':[],'solution':[]}
        # )

        # try:
        #     # if you have never run this before, the exception will be thrown
        #     self.df_word_history = pd.read_csv('./temp_folder/df_word_history.csv')
        # except:
        #     pass
        # c1 = self.df_word_history['date']==get_today_monthday()

        # if len(self.df_word_history[c1])!=1:
        #     # self.df_word_history = get_word_history()
        #     # self.df_word_history = get_combined_word_histories()
        #     # self.df_word_history.to_csv('./temp_folder/df_word_history.csv',index=False)
        #     self.df_word_history =  get_word_history()
        #     self.df_word_history.to_csv('./temp_folder/df_word_history.csv',index=False)

        self.df_word_history =  get_word_history()
        # don't show histories that are in the future
        # try to get this date's word
        # c1 = self.df_word_history['date']==get_today_monthday()        
        # curr_num = self.df_word_history[c1].number.values[0]
        # c2 = self.df_word_history['number']<=curr_num
        # # use the c2 condition to only show word histories before the current monthday
        # self.df_word_history = self.df_word_history[c2]
        # save todays word (solution)
        # self.todays_word = self.df_word_history[c1].solution.values[-1].lower()
        self.todays_word = self.df_word_history.solution.values[0].lower()

    
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

def get_letter_status(your_word,the_word):
    nums =[]
    for i,l in enumerate(list(your_word)):
        if l == the_word[i]:
            nums.append(1)
        elif l in the_word:
            nums.append(2)
        else:
            nums.append(3)
    return nums    

def letter_list_to_str(letter_list):
    return ''.join(
        [str(v) for v in letter_list]
    )
def get_filter(your_word,the_word):
    letter_string = letter_list_to_str(
        get_letter_list(your_word,td_word)
    )
    return your_word + "," + letter_string

def solve(initial_words,solution):
    wdl = wordl()

    # Loop on 5 times, either loading wdl instance with words from the
    #    intial_list array, or by loading the most possible word that
    #    the method wrdlc.filter_words returns (after there are no more intial_words)
    # Also, save the list of possible words at after loading a new word.
    list_df = []
    words_used = []
    letter_status_used = [] 
    for i in range(len(initial_words)):
        w = initial_words[i]
        words_used.append(w)
        letter_status = get_letter_status(w,solution)
        letter_status_used.append(letter_status)
        # Add a word to the wdl instance
        wdl.add_word(w,letter_status)
        wdl_possible_words_json = wdl.try_it() 
        # Append the DataFrame with the list of possible words, at this stage
        df = filter_words(wdl_possible_words_json).dropna().copy()
        df = df[['word','probability']]
        list_df.append(df)
        if len(df)<=1:
            break
    return words_used,letter_status_used,list_df

def solveall(initial_words,solution):
    wdl = wordl()

    # Loop on 5 times, either loading wdl instance with words from the
    #    intial_list array, or by loading the most possible word that
    #    the method wrdlc.filter_words returns (after there are no more intial_words)
    # Also, save the list of possible words at after loading a new word.
    list_df = []
    words_used = []
    letter_status_used = [] 
    for i in range(5):
        if i<len(initial_words):
            w = initial_words[i]
        else:
            # Get last DataFrame from list_df
            df_last = list_df[i-1]
            w = df_last.iloc[0].word
        words_used.append(w)
        letter_status = get_letter_status(w,solution)
        letter_status_used.append(letter_status)
        # Add a word to the wdl instance
        wdl.add_word(w,letter_status)
        wdl_possible_words_json = wdl.try_it() 
        # Append the DataFrame with the list of possible words, at this stage
        df = filter_words(wdl_possible_words_json).dropna().copy()
        df = df[['word','probability']]
        list_df.append(df)
        # if len(df)<=1:
        #     break
        if (len(df)<=1) and (len(words_used)>=len(initial_words)):
            break
    # add solution or last word
    df_last = list_df[-1]
    w = df_last.iloc[0].word
    words_used.append(w)
    letter_status = get_letter_status(w,solution)
    letter_status_used.append(letter_status)

    return words_used,letter_status_used,list_df

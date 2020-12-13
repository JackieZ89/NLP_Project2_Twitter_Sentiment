# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 22:03:10 2020

@author: Jackie
"""

import pandas as pd
import numpy as np
import nltk
import re
import os
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer,PorterStemmer
from nltk.corpus import stopwords
import re
import datetime
lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer() 


#clean text
def remove_emoji(text):
    emoji_pattern = re.compile(
    u"(\ud83d[\ude00-\ude4f])|"  # emoticons
    u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
    u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
    u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
    u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
    "+", flags=re.UNICODE)

    return emoji_pattern.sub(r'', text)


def preprocess(sentence):
    special_marks = ['&', '\n', '@', '$', '#', '☆', '!', '(', ')'
                     ',', '.', ';', ':', '💰', '✅']
    
    sentence=str(sentence)
    sentence = sentence.lower()
    sentence = re.sub('@[^, ]*', '', sentence) #remove twitter user name after @
    for sm in special_marks:
            sentence = sentence.replace(sm, "")
            
    sentence = sentence.replace('{html}',"") 
    sentence = remove_emoji(sentence)
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', sentence)
    rem_url=re.sub(r'http\S+', '',cleantext)
    rem_num = re.sub('[0-9]+', '', rem_url)
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(rem_num)  
    filtered_words = [w for w in tokens if len(w) > 2 if not w in stopwords.words('english')]
    #stem_words=[stemmer.stem(w) for w in filtered_words]
    lemma_words=[lemmatizer.lemmatize(w) for w in filtered_words]
    return " ".join(lemma_words)


def preprocess_tweet(file):
    tweets_df = pd.read_csv(file, index_col=0)
    # drop duplicate
    tweets_df.drop_duplicates(inplace=True)
    
    tweets_df['cleanText']=tweets_df.iloc[:,0].map(lambda s:preprocess(s))
    
    return tweets_df


# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 01:20:47 2020

@author: zhang
"""
from Preprocess_tweets import*
from cal_return_and_senti import*

#load files
example_file = "./tweets/J.P. Morgan.csv"
tweets_df = pd.read_csv(example_file, index_col=0)

tweets_clean = preprocess_tweet(example_file)

JPM_price = pd.read_excel("./stockdata/JPM.xlsx")

JPM_senti = cal_price_senti(JPM_price,tweets_clean)
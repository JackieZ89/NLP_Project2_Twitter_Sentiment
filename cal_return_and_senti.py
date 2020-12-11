# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 01:22:26 2020

@author: zhang

Classify tweets and calculate sentiment scores
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
from textblob import TextBlob
#https://textblob.readthedocs.io/en/dev/


        
def get_sentiment(tweet):
    #use textbolb to get sentiment scores
        analysis = TextBlob(tweet) 
        if analysis.sentiment.polarity > 0: 
            return 'positive'
        elif analysis.sentiment.polarity == 0: 
            return 'neutral'
        else: 
            return 'negative'






         
def classify_sentiment(tweets_clean):
    sentiment = []
    for index, row in tweets_clean.iterrows(): 
        sentiment.append(get_sentiment(row['cleanText']))
    tweets_clean['sentiment'] = sentiment
    
    return tweets_clean
 
def excess_log_return(df,SPY_price, freq = 'H'):
    SPY_price= SPY_price.iloc[::-1]
    SPY_price.rename(columns={"Last Price": "SPY_price", "Volume": "SPY_vol","SMAVG (15)":"SPY_SMAVG"},inplace = True)
    df = df.iloc[::-1] 
    df_all = pd.concat([SPY_price,df], axis=1, join='inner').reindex(SPY_price.index)
    #use specific time interval, e.g every hour
    times = pd.date_range(start='2020-11-23 09:30:00', end='2020-12-08 15:55:00', freq=freq)
    df_all ['filter'] = [True if x in times else False for x in df_all.index]
    df_all = df_all[df_all['filter'] == True]
    #calclulate log return
    df_all['log_return'] = np.log(df_all['Last Price']) - np.log(df_all['Last Price'].shift(1))
    df_all['SPY_log_return'] = np.log(df_all['SPY_price']) - np.log(df_all['SPY_price'].shift(1))
    df_all['excess_log_return'] = df_all['log_return'] - df_all['SPY_log_return']
    return df_all.loc[:,['Last Price','Volume','log_return','excess_log_return']]
 
#把twitter和price的frequency对上, 然后计算每小时的sentiment score
def cal_sentiment_scores(df_price, tweets_classified):
    tweets_classified.index = pd.to_datetime(tweets_classified.index)
    tweets_count = [None]
    sentiment_abs_score = [None]
    sentiment_rela_score = [None]
    df_price = df_price[df_price.index > tweets_classified.index[0]]
    for i in range(len(df_price)-1):
        #todo: 把开头多余的stock 天数去掉
        temp = tweets_classified[(tweets_classified.index > df_price.index[i]) & (tweets_classified.index < df_price.index[i+1])]
        tweets_count.append(len(temp))
        pos_num = len(temp[temp['sentiment']=='positive'])
        neg_num = len(temp[temp['sentiment']=='negative'])

        sentiment_abs_score.append(pos_num - neg_num)
        try:
            sentiment_rela_score.append((pos_num - neg_num)/(pos_num + neg_num))
        except:
            sentiment_rela_score.append(None) #如果分母为0

    df_price.loc[:,'tweets_num'] = tweets_count
    df_price.loc[:,'senti_abs_score'] = sentiment_abs_score
    df_price.loc[:,'senti_rela_score'] = sentiment_rela_score
    return df_price
     
def cal_price_senti(df_price, tweets_clean):
    tweets_classified = classify_sentiment(tweets_clean)
    tweets_classified = tweets_classified[::-1]
    
    SPY_price = pd.read_excel("./stockdata/SPY.xlsx").set_index('Date')#benchmark
    df_price = df_price.set_index('Date')
    df_price = excess_log_return(df_price,SPY_price)  
    df_senti = cal_sentiment_scores(df_price, tweets_classified)
    return df_senti
    

# merge tweet files for the same company, results are in tweets_merged
def merge_twieetfile(root_tweet='./tweets', output_path='./tweets_merged'):
    original_twitter_files = os.listdir(root_tweet)

    company_list = [x.split(" ")[0] for x in original_twitter_files]
    company_list = list(set(company_list))

    merged_df_dict = {}

    for company in company_list:
        merged_df_dict[company] = pd.DataFrame()

    for file in original_twitter_files:
        merged_df_dict[file.split(" ")[0]] = pd.concat([merged_df_dict[file.split(" ")[0]],
                                                        pd.read_csv(root_tweet+'/'+file, index_col=0)])
    # output files
    for company, file in merged_df_dict.items():
        file.drop_duplicates(inplace=True)
        file.to_excel(output_path+'/'+company+'.xlsx')


# calculate sentiment for all companies and save those results
def calculate_sentiment_all_company(root_tweet="./tweets_merged", root_price="./stockdata",
                                    output_path="./statistical_analysis_data"):
    twitter_files = os.listdir(root_tweet)
    price_files = os.listdir(root_price)

    for price_file in price_files:
        if price_file == "SPY.xlsx": continue
        # note here that both price file and tweet file have same name
        df_price = pd.read_excel(root_price + '/' + price_file)
        tweet_file = root_tweet + '/' + price_file

        preprocessed = preprocess_tweet(tweet_file)
        sentiment_added = cal_price_senti(df_price, preprocessed)

        sentiment_added.to_excel(output_path+'/'+price_file)


if __name__ == '__main__':
    merge_twieetfile()
    calculate_sentiment_all_company()
    
    
    
    
    

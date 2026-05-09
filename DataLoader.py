#!/usr/bin/env python
# coding: utf-8

import yfinance as yf

class DataLoader:
    def __init__(self,ticker,from_date,to_date):
        self.ticker = ticker
        self.from_date = from_date
        self.to_date = to_date
        print("Variables are successfully initialised")
    def fetch_data(self):
        ''' Extracts data of a given ticker from Yahoo Finance over a given period'''
        try:
            data = yf.download(self.ticker,start= self.from_date,end=self.to_date)
            if data.empty:
                raise ValueError("No Data Fetched")
            return data
        except Exception as e:
            raise e
    def clean_data(self,data):
        '''Removes null values and arranges stock prices by date'''
        #remove any null or NaN values
        data = data.dropna()
        #Making sure the data is ordered by date
        data = data.sort_index(ascending = True)
        return data
    def get_data(self):
        ''' Fetches raw stock data and returns transformed data of a given ticker over a given period of time'''
        data = self.fetch_data()
        cleaned_data = self.clean_data(data)
        return cleaned_data




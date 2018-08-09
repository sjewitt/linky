import sys
import requests
from requests.auth import HTTPBasicAuth
import html5lib
from bs4 import BeautifulSoup
from pymongo import MongoClient
import csv

def getDB(dbname):
#     client = MongoClient('localhost', 27017)
    return(MongoClient('localhost', 27017)[dbname]) #the database

def getCollection(db,coll):
    return(db[coll])
    

def getResults(parentUrlFilter=None,rawUrlFilter={}):
    print("getting results")
    return(list(collection.find(rawUrlFilter)))
    
def makeCsv(resultList):
    print("making CSV")
    c = resultList
    return()
    
    


if __name__ == '__main__':
    recurseLimit = sys.getrecursionlimit()
    startingurl = "https://tradetest.baxi.co.uk"
    basedomain = ["tradetest.baxi.co.uk","www.baxi.co.uk"]
    client = MongoClient('localhost', 27017)
    db = getDB('linky')
    collection = getCollection(getDB('linky'),'links_raw3')
    data = getResults()
    csvData = makeCsv(data)
    
    
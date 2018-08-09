#NOTE: Shift/3 for hash on RDP on Ubuntu (until I figure out keyboard mapping...)
import sys
import requests
from requests.auth import HTTPBasicAuth
import html5lib
from bs4 import BeautifulSoup
from pymongo import MongoClient


'''
Theres a bug here somewhere that continues looping even if no more links

TODO: MAKE SURE THE LISTS OF LINKS ARE RESET!
Step 1: Insert into queue:
'''

def do_queue_insert_single(uniquelink):
    '''
    Reset parentlist before testing for exists - 
    '''
    parentList = []
    
    exists = db[coll].find({'full_url':uniquelink['full_url']}).count()

    if exists:
        '''
        get matching link. should be just one, but may not be.
        '''
        matches = list(db[coll].find({'full_url':uniquelink['full_url']}))
        parent = matches[0]['parent_url']
        
        if type(parent) is str:
            parentList.append(parent)
            parentList.append(uniquelink['parent_url'])
        if type(parent) is list:
            parent.append(uniquelink['parent_url'])
            parentList = parent
        db[coll].update_many({'full_url':uniquelink['full_url']},{'$set':{'parent_url':parentList}})  
    
    else:
        print('inserting new link: ' + uniquelink['full_url'])
        sourcetag = None    #starting page only
        if 'source_tag' in uniquelink:
            sourcetag = uniquelink['source_tag']
        db[coll].insert({
            'full_url':uniquelink['full_url'],
            'raw_url':uniquelink['raw_url'],
            'parent_url': uniquelink['parent_url'],
            'source_tag': sourcetag,
            'done':False})

def set_done(url):
    db[coll].update_many({'full_url':url},{'$set':{'done':True}})

'''
get links on page:
'''
def do_get_links_from_html(urlString):
#     set_done(urlString)
#     process = False
    
    try:
        set_done(urlString)
        process = False
        
        if basedomain[0] in urlString:
            process = True

        if process:
            urlString = make_full_url(urlString)
            if authuser and authpwd:
                x = requests.get(urlString,auth=HTTPBasicAuth(authuser, authpwd))
            else:
                x = requests.get(urlString)
            soup = BeautifulSoup(x.content,'lxml')
            
            #get all the http resources
            anchors = soup.find_all('a')
            links = soup.find_all('link')
            pics = soup.find_all('img')
#             links=[]
#             pics=[]
            
            anchorlist = []
            actualcount = 0
            for link in links:
                actualcount += 1
                if link.has_attr('href'):
                    full_url = make_full_url(link['href'])
 
                    if full_url:
                        anchorlist.append({'full_url':full_url,'raw_url':link['href'],'parent_url':urlString, 'source_tag':'link'})   #the whole point is to track which URLs are prefixed with HTTP
         
            for anchor in anchors:
                actualcount += 1
                if anchor.has_attr('href'):
                    full_url = make_full_url(anchor['href'])
                    if full_url and has_base_domain(full_url):
                        anchorlist.append({'full_url':full_url,'raw_url':anchor['href'],'parent_url':urlString,'source_tag':'a'})   #the whole point is to track which URLs are prefixed with HTTP

            for pic in pics:
                actualcount += 1
                if pic.has_attr('src'):
                    full_url = make_full_url(pic['src'])
                    if full_url and has_base_domain(full_url):
                        anchorlist.append({'full_url':full_url,'raw_url':pic['src'],'parent_url':urlString,'source_tag':'img'})   #the whole point is to track which URLs are prefixed with HTTP


            cleanlist = []
            for thing in anchorlist:
                append = True
                for thing2 in cleanlist:
                    if thing['full_url'] == thing2['full_url'] and thing['raw_url'] == thing2['raw_url']:
                        append= False
                if append:
                    cleanlist.append(thing)
        
            for uniquelink in cleanlist:
                if uniquelink["full_url"] != urlString:
                    do_queue_insert_single(uniquelink)
                    
        process_links_queued()
    except:
        print('error processing url "' + urlString + '". skipping...')
    
#     process_links_queued()   

def has_base_domain(full_url):
    for base in basedomain:
        if base in full_url:
            return True
    return False

def process_links_queued():

    try:
        link = db[coll].find_one({'done':False})
    
        if 'full_url' in link:
            do_get_links_from_html(link['full_url'])    #only call this if it is FIRST base domain
    
    except:
        print('nothing to process...')        
        
def make_full_url(urlString):

    if '.pdf' in urlString:
        return False
    if '.ico' in urlString:
        return False
    
    if '?' in urlString:                                  #remove querystring. TODO
        urlString = urlString.split('?')[0]
    
    if urlString.startswith('//') and len(urlString) > 2: #absolute, protocol-less
        return(urlString)
    
    if urlString.startswith("/") and len(urlString) > 1:  #relative to root
        return startingurl + urlString
    
    if not urlString.startswith("http"):                  #relative to self
        return startingurl + '/' + urlString
        
    elif urlString == "/":  #root
        return startingurl
    return(urlString)

def start(startingUrl):
    db[coll].drop()
    full_url = make_full_url(startingUrl)
    do_queue_insert_single({'full_url':full_url,'raw_url':'/','parent_url':None})
    do_get_links_from_html(make_full_url(startingUrl))
    
if __name__ == '__main__':
    recurseLimit = sys.getrecursionlimit()
    startingurl = "https://www.jcms-consulting.co.uk"
    basedomain = ["www.jcms-consulting.co.uk","www.eg-designs.uk"]
    coll = 'jcms'
    authuser = None
    authpwd = None
    client = MongoClient('localhost', 27017)
    db = client.linky #the database
    collection = db[coll]
    start(startingurl)
    


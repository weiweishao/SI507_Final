import sqlite3
import requests
import csv
import json
from bs4 import BeautifulSoup
from secrets import *

import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO



# ============================ Part 1  ===================================
# in this part I crawl the 'Ann Arbor with Kids' website and
# retrieve events information using cache
# I also get event gps location using Google places API and save them using cache

CACHE_FNAME1 = 'events_cache.json'
try:
    cache_file1 = open(CACHE_FNAME1, 'r')
    cache_contents1 = cache_file1.read()
    CACHE_DICTION1 = json.loads(cache_contents1)
    cache_file1.close()
except:
    CACHE_DICTION1 = {}

CACHE_FNAME2 = 'orgs_cache.json'
try:
    cache_file2 = open(CACHE_FNAME2, 'r')
    cache_contents2 = cache_file2.read()
    CACHE_DICTION2 = json.loads(cache_contents2)
    cache_file2.close()
except:
    CACHE_DICTION2 = {}



# helper function to get event gps location
def compose_url_location(address):
    baseurl = 'https://maps.googleapis.com/maps/api/place/findplacefromtext'
    params={}
    params['input']=address
    params['inputtype']='textquery'
    params['fields']='geometry'
    temp_list = []
    for i in params:
        temp_list.append(str(i) + "=" + str(params[i]).replace(" ", "%20"))
        parameter_string = "&".join(temp_list)
    return baseurl+"/json?{}&key={}".format(parameter_string, google_places_key)

def get_event_gps_location(address):
    resp_text = requests.get( compose_url_location(address)).text
    resp_json = json.loads(resp_text)
    try:
        location = resp_json['candidates'][0]['geometry']['location']
    except:
        location = {}
    return location
            

# parameter: 2 strings representing the age range and date
# can be 'b' 't' 'p' 'e'
# return: a list of event info
def get_event_info(age_range, plan_date):
    baseurl = 'https://annarborwithkids.com/events/categories/age-range/'
    if age_range == 'b':
        age = 'babies'
    elif age_range == 't':
        age = 'toddlers'
    elif age_range == 'p':
        age = 'preschoolers'
    elif age_range == 'e':
        age = 'elementary-events'

    url = baseurl + age
    rsq_text = requests.get(url).text
    rsq_soup = BeautifulSoup(rsq_text,'html.parser')
    events_table = rsq_soup.find('table',{'class':'events-table'})
    events_info = events_table.find_all('td')

    events = []
    for i in range(int(len(events_info)/2)):
        date = events_info[i*2].text.split()[0]
        # format: '12/05/2018'
        time = events_info[i*2].text.split()[1:]
        # format: ['All','Day'] or ['2:30pm-5:30pm']
        name = events_info[(i*2+1)].text[1:-1].split('\n')[0]
        # a string of the event name, 'Everyday Indoor Activities'
        url = events_info[(i*2+1)].find("a")['href']
        # url of event page
        age_range = age

        # filter boilerplate event
        if name not in ['Everyday Indoor Activities','Everyday Outdoor Activities','Kids Eat Free'] and date == plan_date:
            # crawl another layer to get event detail
            event_text = requests.get(url).text
            event_soup = BeautifulSoup(event_text, 'html.parser')
            event_detail = event_soup.find_all('p')[1].find_all('p')[0].text
            org = event_detail.split('\n')[2]
            address = event_detail.split('\n')[-2].lstrip()
            desc =event_soup.find_all('p')[1].find_all('p')[1].text.split('\n')[0]
            loc = get_event_gps_location()
            event = {'name':name, 'time':time,
                     'url':url, 'address':address, 'org':org, 'loc':loc, 'desc':desc}
            events.append(event)      
    return events

# parameter: a string of age_range, a date 'MM/DD/YYYY'
# return: the program will save the search results using cache
def get_event_info_using_cache(age_range,plan_date):
    
    unique_ident = plan_date + age_range
    results = {}

    if unique_ident in CACHE_DICTION1:
        print('Getting cached data...')
        return CACHE_DICTION1[unique_ident]

    else:
        print('Making request for new data...')
        results = get_event_info(age_range, plan_date)

        CACHE_DICTION1[unique_ident] = results
        dumped_json_cache = json.dumps(CACHE_DICTION1,indent=4)
        fw = open(CACHE_FNAME1,"w")
        fw.write(dumped_json_cache)
        fw.close() 

    return CACHE_DICTION1[unique_ident]
            
            

# return: crawl AA with kids and save the orgs in a cached file
# format: (org_name, org_url, org_location)
def get_orgs_using_cache():
    result = {}
    fw = open(CACHE_FNAME2,"w")
    url = 'https://annarborwithkids.com/locations/'
    orgs_text = requests.get(url).text
    orgs_soup = BeautifulSoup(orgs_text, 'html.parser')
    orgs_info = orgs_soup.find('ul',{'class':'em-locations-list'}).find_all('li')
    
    for i in range(int(len(orgs_info)/2)):
        name = orgs_info[2*i].find('a').text
        url = orgs_info[2*i].find('a')['href']
        address = orgs_info[(2*i+1)].text
        if name not in CACHE_DICTION2:
            CACHE_DICTION2[name] = {'url':url, 'address':address}

    dumped_json_cache = json.dumps(CACHE_DICTION2,indent=4)
    fw.write(dumped_json_cache)
    fw.close() 



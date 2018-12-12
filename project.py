import sqlite3
import requests
import csv
import json
from bs4 import BeautifulSoup
from secrets import *

import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import plotly.plotly as py
import plotly.graph_objs as go
import webbrowser

DBNAME = 'data.db'
# =========================== Part 3 ====================================
# in this part I get pictures using Bing Image Search API for event

def get_event_pic(event_name):
    subscription_key = B_key_2
    search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
    search_term = event_name.lower()

    headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
    params  = {"q": search_term, "license": "public", "imageType": "photo"}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()

    thumbnail_urls = [img["thumbnailUrl"] for img in search_results["value"][:4]]
    return thumbnail_urls


def print_pic(event_name):
    thumbnail_urls = get_event_pic(event_name)
    size = len(thumbnail_urls)

    if size == 0:
        print('Sorry. No past photos found.')
    else:
        w=10
        h=10
        fig=plt.figure(figsize=(6, 8))
        columns = 1
        rows = size
        for i in range(1,(size+1)):
            image_data = requests.get(thumbnail_urls[i-1])
            image = Image.open(BytesIO(image_data.content))
            fig.add_subplot(rows, columns, i)
            plt.imshow(image)
        plt.show()



# =========================== Part 4 ====================================
# in this part I create Class Event for interactive program
# and also other functions that help display events neatly


# class events
class Events():
    def __init__(self, name, date, time, url, org, loc, desc, lat, lng):
        self.name = name
        self.date = date
        self.time = time
        self.url = url
        self.org = org
        self.loc = loc
        self.desc = desc
        self.lat = lat
        self.lng = lng

    def __str__(self):
        return (self.name + ': [' +self.date + '] (' +self.time + ') @ ' + self.loc)


def ask_for_input():
    raw_input = str(input("\nEnter command: "))
    save_input = raw_input.lower().split()
    return save_input
    

# this function handles error input and return a list of [age, date]
def get_age_date(answer):
    
    age_lst = ['baby','toddler','preschool','elementary']
    date_lst = ['12/11/2018','12/12/2018','12/13/2018','12/14/2018','12/15/2018']
    age = answer[0]
    date = answer[1]
    if age in age_lst and date in date_lst:
        return [age, date]
    else:
        return []


# parameter: [age,date]
# return: a list of events instance
def print_events_for_age_date(age_date_lst):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    age = age_date_lst[0][0]
    date = age_date_lst[1]
    results = []

    stm = '''
        SELECT Events.Name, Events.Date, Events.Time, Events.Url, Events.Org,
        Events.Location, Events.Desc, Locs.lat, Locs.Lgt
        FROM Events Join Locs
        On Events.LocId = Locs.Id
        WHERE Age = ? and Date = ?
        '''
    insertion = (age, date)
    cur.execute(stm, insertion)

    for c in cur:
        name = c[0]
        date = c[1]
        time = c[2]
        url = c[3]
        org = c[4]
        loc = c[5]
        desc = c[6]
        lat = c[7]
        lng = c[8]
        event = Events(name, date, time, url, org, loc, desc, lat, lng)
        results.append(event)
    conn.close()

    i=1
    for i in range( len(results)):
        print(i+1, results[i].__str__())
    return results



def plot_map_for_age_date(event_instance_lst):
    # get gps lat and lgt for all events in the list
    lats = []
    lngs = []
    texts = []
    for e in event_instance_lst:
        lats.append(float(e.lat))
        lngs.append(float(e.lng))
        texts.append(e.name)
    # get edge locations
    lat_max = -1000
    lat_min = 1000
    lng_max = -1000
    lng_min = 1000
    for i in range(len(lats)):
        if lats[i] > lat_max:
            lat_max = lats[i]
        if lats[i] < lat_min:
            lat_min = lats[i]
        if lngs[i] < lng_min:
            lng_min = lngs[i]
        if lngs[i] > lng_max:
            lng_max = lngs[i]
    axis = [lat_min-0.3, lat_max+0.3, lng_min-0.3, lng_max+0.3]

    lat_axis = [axis[0], axis[1] ]
    lon_axis = [axis[2], axis[3] ]
    center_lat = ( axis[0] + axis[1] )/2
    center_lon = ( axis[2] + axis[3] )/2
    title = 'Family Events in Ann Arbor'

    data = [ dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = lngs,
        lat = lats,
        text = texts,
        mode = 'markers',
        marker = dict(
            size = 8,
            symbol = 'star',
        ))]
    
    layout = dict(
        title = title,
        geo = dict(
            scope='usa',
            projection=dict( type='albers usa' ),
            showland = True,
            landcolor = "rgb(250, 250, 250)",
            subunitcolor = "rgb(100, 217, 217)",
            countrycolor = "rgb(217, 100, 217)",
            lataxis = {'range': lat_axis},
            lonaxis = {'range': lon_axis},
            center= {'lat': center_lat, 'lon': center_lon },
            countrywidth = 3,
            subunitwidth = 3
        ),
    )

    fig = dict(data=data, layout=layout)
    py.plot(fig, filename = title)



def get_number_range(event_instance_lst):
    size = len(event_instance_lst)
    nums = []
    for i in range(size):
        nums.append(str(i+1))
    return nums

# parameter: an integer - number representing the event
# parameter: a list of events instances - results from get_events_for_age_date()
def get_event_detail(event_instance_lst, answer_number):
    event = event_instance_lst[(int(answer_number)-1)]
    event_name = event.name
    event_url = event.url
    print('Getting detail information and past pictures')
    webbrowser.open(event_url)
    print_pic(event_name)

def print_help():
    print('             ')
    print('    <age> <date>')
    print('        available anytime')
    print('        lists all events for a given age on a given date')
    print('        valid inputs: ')
    print('            for age: baby, toddler, preschool, elementary')
    print('            for date: MM/DD/YYYY for the next 5 days')
    print('    detail <result_number>')
    print('        available only if there is an active result set')
    print('        opens the event website and displays 4 pictures from past event')
    print('        valid inputs: on interger 1-len(result_set_size)')
    print("    map")
    print('        available only if there is an active events list')
    print('        displays the current results on a map')
    print('    exit')
    print('        exists the program')
    print('    help')
    print('        lists available commends (these instructions)')
    print('                    ')



# =========================== Part 5 ====================================
# this is the part for interactive program

def interactive():
    command = ['map', 'detail', 'exit', 'help']
    age_lst = ['baby','toddler','preschool','elementary']
    date_lst = ['12/11/2018','12/12/2018','12/13/2018','12/14/2018','12/15/2018']
    state = "Let's plan for some family fun! Tell us about your child's age range and the date."
    state += "\nOptions for age: baby, toddler, preschool, elementary."
    state += "\nOptions for date: (MM/DD/YYYY) one of the next 5 days."
    print(state)

    answer = ask_for_input()
    if len(answer)==2 and answer[0] in age_lst and answer[1] in date_lst:
        age_date_lst = get_age_date(answer)
        save = print_events_for_age_date(age_date_lst)
        nums = get_number_range(save)
        answer = ask_for_input()
        
    elif answer[0] == 'exit':
        print('Bye!')
        pass
    elif answer[0] == 'help':
        print_help()
        answer = ask_for_input()
    else:
        print('\nSorry, this is not valid input.')
        answer = ask_for_input()
        
    
    while answer[0] != 'exit':
        
        if answer[0] == 'map':
            plot_map_for_age_date(save)
            answer = ask_for_input()

        elif answer[0] == 'help':
            print_help()
            answer = ask_for_input()
            
        elif answer[0] == 'detail' and answer[1] in nums:
            get_event_detail(save, answer[1])
            answer = ask_for_input()

        elif answer[0] in age_lst and answer[1] in date_lst:
            age_date_lst = get_age_date(answer)
            save = print_events_for_age_date(answer)
            nums = get_number_range(save)
            answer = ask_for_input()
            
        else:
            print('\nSorry, this is not valid input.')
            answer = ask_for_input()

    if answer == 'exit':
        print('Bye!')
        pass



interactive()

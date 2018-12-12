import sqlite3
import requests
import csv
import json
from bs4 import BeautifulSoup
from secrets import *


# ============================ Part 2 ====================================
# in this part I create a database to save the cached results
DBNAME = 'data.db'
DATA1 = 'events_cache.json'
DATA2 = 'orgs_cache.json'

def create_db():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = '''
        DROP TABLE IF EXISTS 'Events';
        '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        DROP TABLE IF EXISTS 'Orgs';
        '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        DROP TABLE IF EXISTS 'Locs';
        '''
    cur.execute(statement)
    conn.commit()

    # create table: Events
    statement = '''
        CREATE TABLE 'Events' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT NOT NULL,
            'Date' TEXT NOT NULL,
            'Time' TEXT NOT NULL,
            'Age' TEXT NOT NULL,
            'Url' TEXT NOT NULL,
            'Org' TEXT NOT NULL,
            'Location' TEXT NOT NULL,
            'LocId' INTEGER,
            'Desc' TEXT
        );
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'Locs' (
            'id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Address' TEXT NOT NULL,
            'Lat' TEXT NOT NULL,
            'Lgt' TEXT NOT NULL
        );
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'Orgs' (
            'id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT NOT NULL,
            'Address' TEXT NOT NULL,
            'url' TEXT NOT NULL
        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()


def populate_events():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    # from DATA1 write raw data into Events
    # Table Events not complete, 2 foreign ids to be filled
    with open(DATA1) as e_data:
        e_json = json.load(e_data)
        for date_age in e_json:
            for i in e_json[date_age]:
                date = date_age[:-1]
                age = date_age[-1]
                name = i['name']
                time = i['time'][0]
                url = i['url']
                address = i['address']
                org = i['org']
                desc = i['desc']
                insertion = (name, date, time, age, url, org, address, desc)
                statement = '''
                    INSERT INTO 'Events'
                    (Name, Date, Time, Age, Url, Org, Location, Desc) 
                    VALUES (?,?,?,?,?,?,?,?)
                    '''
                cur.execute(statement, insertion)
                conn.commit()
    conn.close()



def populate_orgs():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    # from DATA2 write raw data into Events
    with open(DATA2) as o_data:
        o_json = json.load(o_data)
        for org in o_json:
            name = org
            url = o_json[org]['url']
            address = o_json[org]['address']
            insertion = (name, address, url)
            statement = '''
                    INSERT INTO 'Orgs' (Name, Address, Url) 
                    VALUES (?,?,?)
                    '''
            cur.execute(statement, insertion)
            conn.commit()
    conn.close()

def populate_locs():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    # from DATA1 write raw data into Locs
    locations = {}
    with open(DATA1) as e_data:
        e_json = json.load(e_data)
        for date_age in e_json:
            for i in e_json[date_age]:
                location = i['address']
                if location not in locations:
                    
                    lat = i['loc']['lat']
                    lng = i['loc']['lng']
                    locations[location]=[lat,lng]

    for address in locations:
        name = address
        lat = locations[address][0]
        lng = locations[address][1]
        insertion = (name, lat, lng)
        statement = '''INSERT INTO 'Locs'
                    (Address, Lat, Lgt) VALUES (?,?,?)'''
        cur.execute(statement, insertion)
        conn.commit()
    conn.close()



    
def insert_location_id():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = '''
        Select Events.id, Events.Location, Locs.Id, Locs.Address
        From Events JOIN Locs
        On Events.Location = Locs.Address
        '''
    cur.execute(statement)
    link = []
    for c in cur:
        link.append(c)

    for row in link:
        insertion = (row[2], row[0])
        statement = '''UPDATE Events
                SET LocId = ? WHERE Id = ?'''
        cur.execute(statement, insertion)
        conn.commit()
    conn.close()

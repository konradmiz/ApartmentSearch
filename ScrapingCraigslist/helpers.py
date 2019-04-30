# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 20:13:30 2019

@author: Konrad
"""

import time
import requests
from bs4 import BeautifulSoup as bs4
from requests_html import HTMLSession
import pandas as pd
import random
import string
from slackclient import SlackClient
import numpy as np

def get_apt_list():
    regions = ['sfc', 'eby', 'pen', 'sby']
    all_apts = []

    for region in regions:
        all_apts.append(get_apartments_html(region))
        time.sleep(1.1)
        
    all_apts = [item for sublist in all_apts for item in sublist]

    return all_apts

def get_apartments_html(region):
    session = HTMLSession()
    
    url_base = f'https://sfbay.craigslist.org/search/{region}/apa?sort=date&hasPic=1&housing_type=1&housing_type=10&housing_type=2&housing_type=3&housing_type=4&housing_type=5&housing_type=6&housing_type=8&housing_type=9&max_bedrooms=2&max_price=3000&minSqft=500&min_price=1000'
    craigslist_response = session.get(url_base)

    a_href = craigslist_response.html.find('p')

    apt_list = [a.find('a')[0].absolute_links for a in a_href]
    url_list_lists = [list(a) for a in apt_list]
    flat_list = [item for sublist in url_list_lists for item in sublist]
    
    return flat_list

def parse_geog(html):
    
    city = ""
    for tag in html.find_all("meta"):
        if tag.get("name", None) == "geo.placename":
            city = string.capwords(tag.get("content", None))
            
    try:
        street_address = html.find("div", attrs = {'class': 'mapaddress'}).text
    except:
        street_address = ""
        
    one_apt_loc = html.find_all('div', attrs = {'class' : 'viewposting'})[0]
    loc_df = pd.DataFrame({'city' : city,
                          'lat': float(one_apt_loc['data-latitude']),
                          'lon': float(one_apt_loc['data-longitude']),
                          'address': street_address}, 
                          index = [0])
    return loc_df

def parse_extra(html):
    
    try: 
        cats_allowed = str(html.find_all('p', {'class': 'attrgroup'})[1]).find('cats are')    
        cats = True if cats_allowed != -1 else None
    except:
        cats = None
    
    try:
        dogs_allowed = str(html.find_all('p', {'class': 'attrgroup'})[1]).find('dogs are')
        dogs = True if dogs_allowed != -1 else None
    except:
        dogs = None

    try:
        furnished_there = str(html.find_all('p', {'class': 'attrgroup'})[1]).find('furnished')
        furnished = True if furnished_there != -1 else None
    except:
        furnished = None
    
    try:
        housing_info = html.find_all('p', {'class': "attrgroup"})[1].text
        
        if housing_info.find('apartment') != -1:
            housing_type = 'apartment'
        elif housing_info.find('townhouse') != -1:
            housing_type = 'townhouse'
        elif housing_info.find('house') != -1:
            housing_type = 'house'
        elif housing_info.find('condo') != -1:
            housing_type = 'condo'
        elif housing_info.find('duplex') != -1:
            housing_type = 'duplex'
        elif housing_info.find('cottage') != -1:
            housing_type = 'cottage'
        elif housing_info.find('flat') != -1:
            housing_type = 'flat'
        elif housing_info.find('loft') != -1:
            housing_type = 'loft'
        else:
            housing_type = ''
    except:
        housing_type = ''
    
    try:
        laundry_info = html.find_all('p', {'class': "attrgroup"})[1].text

        if laundry_info.find('laundry in bldg') != -1:
            laundry = "laundry_in_bldg"
        elif laundry_info.find('laundry on site') != -1:
            laundry = "laundry_on_site"
        elif laundry_info.find('no laundry on site') != -1:
            laundry = "no_laundry_on_site"
        elif laundry_info.find('w/d in unit') != -1:
            laundry = 'wd_in_unit'
        elif laundry_info.find('w/d hookups') != -1:
            laundry = 'wd_hookups'
        else:
            laundry = ''
    except:
        laundry = ''
        
    extra_info = pd.DataFrame({'cats' : cats,
                              'dogs' : dogs,
                              'laundry' : laundry,
                              'housing_type' : housing_type,
                              'furnished' : furnished}, index = [0])
    return extra_info

def parse_basics(html):
    
    try:
        # bed_bath format: "3 BR / 2 BA"
        bed_bath = html.find('span', {'class' : 'shared-line-bubble'}).text.lower().split("/") 
        
        bed = bed_bath[0].strip().replace('br', '')
        bath = bed_bath[1].strip().replace('ba', '')
        
        if bed == "":
            bed = np.NaN
        else:
            bed = int(bed)
            
        if bath == "":
            bath = np.NaN
        else:
            bath = int(bath)
        
    except: 
        bed = np.NaN
        bath = np.NaN
        
    try:
        price = html.find('span', attrs = {'class' : 'price'}).text.replace("$", "")
        if price == "":
            price = np.NaN
        else:
            price = int(price)
    except:
        price = np.NaN
    
    try:
        sqft = int(html.find_all('span', {'class' : 'shared-line-bubble'})[1].text.replace("ft2", ""))
        if sqft == "":
            sqft = np.NaN
        else:
            sqft = int(sqft)
    except:
        sqft = np.NaN
    
    try:
        num_pics = html.find("span", attrs = {'class' : 'slider-info'}).text.replace("image 1 of ", "")
        if num_pics == "":
            num_pics = np.NaN
        else:
            num_pics = int(num_pics)
    except:
        num_pics = np.NaN
        
    try:
        url = html.find('link')['href']
    except:
        url = ""   
        
    try:
        title = html.find('title').text.replace("- apts/housing for rent - apartment rent", "").strip()
    except:
        title = ""
        
    try:
        description = str(html.find('section', {'id' : 'postingbody'}).text).replace("\n\nQR Code Link to This Post\n\n\n", "").strip()
    except:
        description = ""

    try:
        contact_info = True if html.text.find('show contact info') != -1 else False
    except: 
        contact_info = ""

    try:
        post_time = html.find_all('p', {'class': 'postinginfo'})[0].text.replace("\n", "").replace("Posted", "").strip()
    except:
        post_time = ""
    
    basic_info = pd.DataFrame({'bed' : bed,
                       'bath' : bath,
                       'price': price,
                       'sqft' : sqft,
                       'num_pics' : num_pics,
                       'url' : url,
                       'title' : title,
                       'description' : description,
                       'contact info' : contact_info,
                       'post_time': post_time}, index = [0])
            
    return basic_info

        
def parse_listing(html_link):
    one_apt = requests.get(html_link)
    html = bs4(one_apt.text, "html.parser")
    
    posting_id = html_link.split('/')[-1].replace('.html', "")
    
    basic_info = parse_basics(html)
    loc_df = parse_geog(html)
    extra_df = parse_extra(html)
    
    apt_df = pd.concat([basic_info, loc_df, extra_df], axis = 1)
    apt_df['posting_id'] = posting_id
        
    return(apt_df)
    
def run_parsing(urls):
    df_list = []
    
    for i in range(len(urls)):
        df_list.append(parse_listing(urls[i]))
        time.sleep(1 + random.uniform(-1, 1))
        
    entire_df = pd.concat(df_list)
    return entire_df

def add_url(sc, price, bedrooms, bathrooms, city, url):
    
    sc.api_call(
      "chat.postMessage",
      channel="housing",
      text=f"Do you like this apartment? \n ${price} \\ {city} \nBed: {bedrooms} \\ Bath: {bathrooms} ",
      attachments = [{
                "text": url,
                "callback_id": "wopr_game",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "Yes",
                        "text": "Yes",
                        "type": "button",
                        "value": "yes"
                    },
                    {
                        "name": "No",
                        "text": "No",
                        "type": "button",
                        "value": "no"
                    }
                ]
            }]
    )


def post_new_apts(my_df, engine, current_date):
    
    try:
        my_df['posting_id'].to_sql(name = "temp", if_exists = "replace", con = engine)
        unseen_ids = pd.read_sql('SELECT * FROM temp WHERE "posting_id" NOT IN (SELECT "posting_id" FROM apts)', engine)['posting_id'].values

        new_apts = my_df[my_df['posting_id'].isin(unseen_ids)]
        new_apts.loc[:, 'upload_time'] = str(current_date.strftime("%Y-%m-%d %H:%M:%S"))
        new_apts['upload_time'] = pd.to_datetime(new_apts['upload_time'])
        new_apts.to_sql(name = "apts", if_exists = "append", con = engine)
    except:
        my_df.loc[:, 'upload_time'] = str(current_date.strftime("%Y-%m-%d %H:%M:%S"))
        my_df['upload_time'] = pd.to_datetime(my_df['upload_time'])
        my_df.to_sql(name = "apts", if_exists = "append", con = engine)


#def post_to_slack(apt_df, slack_token):
#
#    sc = SlackClient(slack_token)
#    
#    for idx, row in apt_df.iloc[:2, ].iterrows():
#    
#        price = row['price']
#        bedrooms = row['bed']
#        bathrooms = row['bath']
#        city = row['city']
#        url = row['url']
#        
#        add_url(sc, price, bedrooms, bathrooms, city, url)

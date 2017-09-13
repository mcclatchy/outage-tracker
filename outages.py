import os
import sys
import time
from datetime import datetime
import requests
import json
import boto3
import xml.etree.ElementTree as ET


def add_to_s3(data, state_postal):
    ## connect to S3
    s3 = boto3.resource('s3')

    ## set the file name based on the sheet id
    filename_s3 = 'data/outages/%s.json' % (state_postal)

    ## upload the string of json
    s3.Object('mccdata', filename_s3).put(Body=data)

    ## cdn domain for file url
    domain = 'https://d1at6jy1u029jl.cloudfront.net'

    ## url of the uploaded file
    url = domain + '/' + filename_s3

    print("\nJSON uploaded to S3:\n%s\n" % url)


def fpl_api():
    state_postal = "FL"

    #### GRAB DATA ####

    ## set the source
    url = 'http://www.fplmaps.com/data/storm-outages.js'
    ## get the data
    response_text = requests.get(url).text
    ## fix the json
    json_all = json.loads(response_text[7:-2])
    ## put out the counties
    counties = json_all['counties']

    #### CONVERT DATA ####

    ## loop through and create a new json structure
    json_list = []
    for county, properties in counties.items():
        name = properties['name'] 
        outages = properties['numberofoutages']
        total = properties['numberofaccounts']
        try:
            percent = round(outages/total*100, 2)
        except:
            percent = 'N/A'
        dictionary = {
            'location': name,
            'outages': outages,
            'total': total,
            'percent': percent
        }
        json_list.append(dictionary)
    ## put the list of counties into a dict for counties
    state_file = {'counties': json_list}
    ## convert it to json object
    data = json.dumps(state_file)

    #### ADD TO S3 ####
    add_to_s3(data, state_postal)


def gpc_api():
    state_postal = "GA"

    #### FIND DIRECTORY ####

    current_time = int(time.time())
    # current_time = 1505234387 ## test
    interval_url = 'http://outagemap.georgiapower.com/external/data/interval_generation_data/metadata.xml?timestamp={}'.format(current_time)
    ## grab the xml as text
    interval_response = requests.get(interval_url).text
    ## convert it Python-native XML
    interval_xml = ET.fromstring(interval_response)
    ## grab the interval directory
    interval_directory = interval_xml[0].text

    #### GET DATA ####

    ## construct API URL
    api_types = ['', '2']
    # api_type = 2 ## zip code
    # api_type = '' ## county

    for api_type in api_types:
        api_url = 'http://outagemap.georgiapower.com/external/data/interval_generation_data/{}/report{}.js'.format(interval_directory, api_type)
        ## grab the data response
        api_response = requests.get(api_url)
        ## get the json
        api_json = api_response.json()
        ## filter the json
        items = api_json['file_data']['curr_custs_aff']['areas'][0]['areas']

        #### CONVERT DATA ####
        json_list = []
        for item in items:
            if api_type == '2':
                zip_code = item['area_name']
                city = item['area_name_alias']
            else:
                county = item['area_name']
            outages = item['custs_out']
            total = item['total_custs']
            try:
                percent = round(outages/total*100, 2)
            except:
                percent = 'N/A'
            if api_type == '2':
                dictionary = {
                    'location': zip_code,
                    'city': city.title(),
                    'outages': outages,
                    'total': total,
                    'percent': percent
                }
            else:
                dictionary = {
                    'location': county.title(),
                    'outages': outages,
                    'total': total,
                    'percent': percent
                }
            json_list.append(dictionary)

        if api_type == '2':
            zip_json = json_list
        else:
            county_json = json_list

    ## put the list of counties into a dict for counties
    state_file = {
        'counties': county_json, 
        'zips': zip_json
    }
    ## convert it to json object
    data = json.dumps(state_file)

    #### ADD TO S3 ####
    add_to_s3(data, state_postal)


def download():
    message = '------- FL/GA POWER OUTAGE SCRAPER ------'
    print(message)

    start_time = datetime.now()

    start_message = '\nStarted:\t\t' + time.ctime() + '\n'

    message = start_message
    print(message)

    ## execute the functions
    try:
        fpl_api()
    except:
        message = 'FPL scrape failed: \n' + str(sys.exc_info())
        print(message)
    try:
        gpc_api()
    except:
        message = 'GPC scrape failed: \n' + str(sys.exc_info())
        print(message)

    end_time = datetime.now()

    end_message = '\nFinished:\t' + time.ctime() + '\n\n'
    bake_length = str(end_time - start_time) 

    message = end_message
    print(message)

    message = 'length:\t\t' + bake_length
    print(message)
    message = '--------------------------------------------------\n'
    print(message)


download()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 13:43:18 2024

@author: jbc0102
"""

import requests
import hashlib
import random
import pandas as pd

def save_to_excel(data, excel_file):
    try:
        existing_df = pd.read_excel(excel_file)
    except FileNotFoundError:
        existing_df = pd.DataFrame()

    new_df = pd.DataFrame([data])

    if existing_df.empty:
        updated_df = new_df.copy()
    else:
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    
    if '_id' in updated_df.columns:
        updated_df = updated_df.drop(columns='_id')

    updated_df.to_excel(excel_file, index=False, engine='openpyxl')
    

def create_data(dictItem, typeItem, excel_path):
    data_list = []
    # create a new dictionary with the id, type, and data fields
    new_dict = {
        'type': typeItem,
        'data': dictItem
      }           
        # append the new dictionary to the output list
    save_to_excel(new_dict, excel_path)
    return data_list 

def df_fitbit(activity, base_date, end_date, keys, intradays=False):
    if intradays:
        apiCall = '/1.2/user/-/{}/date/{}/1d/15min.json'.format(activity, base_date)    
    else:
        apiCall = '/1.2/user/-/{}/date/{}/{}.json'.format(activity, base_date, end_date)
    
    headers = {'Authorization': 'Bearer {}'.format(keys['access_token'])}
    final_url = 'https://api.fitbit.com' + apiCall
    resp = requests.get(final_url, headers=headers)
    resp = resp.json()
    return resp

def make_zero_sleep(base_date, end_date, collection):
    sleepStageDict = {
        "dateTime": base_date.strftime("%Y-%m-%d"),
        "value": []
        }
    for h in range(21, 24):
        for m in range(0, 60, 15):
            time_str = '{} {:02d}:{:02d}:00'.format(base_date.strftime("%Y-%m-%d"), h, m)
            sleepStageDict['value'].append({'dateTime': time_str, 'level': 'none', 'seconds': 0})   
    
    for h in range(0, 10):
        for m in range(0, 60, 15):
            time_str = '{} {:02d}:{:02d}:00'.format(end_date, h, m)
            sleepStageDict['value'].append({'dateTime': time_str, 'level': 'none', 'seconds': 0})   
            if h == 9 and m == 0:
                break
    create_data(sleepStageDict, "sleep_stage", collection)
    
    startTimeDict = {
        "dateTime": base_date.strftime("%Y-%m-%d"),
        "value": 0
    }
    create_data(startTimeDict,"sleep_startTime", collection)

    endTimeDict = {
        "dateTime": base_date.strftime("%Y-%m-%d"),
        "value": 0
    }
    create_data(endTimeDict,"sleep_endTime", collection)

    timeInBedDict = {
        "dateTime": base_date.strftime("%Y-%m-%d"),
        "value": 0
    }
    create_data(timeInBedDict,"timeInBed", collection)

    minutesAsleepDict = {
        "dateTime": base_date.strftime("%Y-%m-%d"),
        "value": 0
    }
    create_data(minutesAsleepDict,"minutesAsleep", collection)

    minutesAwakeDict = {
        "dateTime": base_date.strftime("%Y-%m-%d"),
        "value": 0
    }
    create_data(minutesAwakeDict,"minutesAwake", collection)

    efficiencyDict = {
        "dateTime": base_date.strftime("%Y-%m-%d"),
        "value": 0
    }
    create_data(efficiencyDict,"sleep_efficiency", collection)

    summaryDeepDict = {
        "dateTime": base_date.strftime("%Y-%m-%d"),
        "value": 0
    }
    create_data(summaryDeepDict,"sleep_Deep", collection)

    summaryLightDict = {
        "dateTime": base_date.strftime("%Y-%m-%d"),
        "value": 0
    }
    create_data(summaryLightDict,"sleep_Light", collection)

    summaryRemDict = {
        "dateTime": base_date.strftime("%Y-%m-%d"),
        "value": 0
    }
    create_data(summaryRemDict,"sleep_Rem", collection)

    summaryWakeDict = {
        "dateTime": base_date.strftime("%Y-%m-%d"),
        "value": 0
    }
    create_data(summaryWakeDict,"sleep_Wake", collection)


def getSleepData(base_date, end_date, token, collection):
    sleepList = df_fitbit('sleep', base_date, end_date, token)['sleep']
    if not sleepList:
        make_zero_sleep(base_date, end_date, collection)
    else:
        for sleepItem in sleepList:
            mainSleep = sleepItem['isMainSleep']
            if mainSleep == True and sleepItem['dateOfSleep'] == end_date.strftime("%Y-%m-%d"):
                if 'levels' in sleepItem and 'summary' in sleepItem['levels'] and 'deep' in sleepItem['levels']['summary'] and 'minutes' in sleepItem['levels']['summary']['deep']:
                    sleepStageDict = {
                        "dateTime": sleepItem['dateOfSleep'],
                        "value": sleepItem['levels']['data']
                    }
                    create_data(sleepStageDict, "sleep_stage", collection)
                    
                    startTimeDict = {
                        "dateTime": sleepItem['dateOfSleep'],
                        "value": sleepItem['startTime']
                    }
                    create_data(startTimeDict,"sleep_startTime", collection)
        
                    endTimeDict = {
                        "dateTime": sleepItem['dateOfSleep'],
                        "value": sleepItem['endTime']
                    }
                    create_data(endTimeDict,"sleep_endTime", collection)
        
                    timeInBedDict = {
                        "dateTime": sleepItem['dateOfSleep'],
                        "value": sleepItem['timeInBed']
                    }
                    create_data(timeInBedDict,"timeInBed", collection)
        
                    minutesAsleepDict = {
                        "dateTime": sleepItem['dateOfSleep'],
                        "value": sleepItem['minutesAsleep']
                    }
                    create_data(minutesAsleepDict,"minutesAsleep", collection)
        
                    minutesAwakeDict = {
                        "dateTime": sleepItem['dateOfSleep'],
                        "value": sleepItem['minutesAwake']
                    }
                    create_data(minutesAwakeDict,"minutesAwake", collection)
        
                    efficiencyDict = {
                        "dateTime": sleepItem['dateOfSleep'],
                        "value": sleepItem['efficiency']
                    }
                    create_data(efficiencyDict,"sleep_efficiency", collection)
        
                    summaryDeepDict = {
                        "dateTime": sleepItem['dateOfSleep'],
                        "value": sleepItem['levels']['summary']['deep']['minutes']
                    }
                    create_data(summaryDeepDict,"sleep_Deep", collection)
        
                    summaryLightDict = {
                        "dateTime": sleepItem['dateOfSleep'],
                        "value": sleepItem['levels']['summary']['light']['minutes']
                    }
                    create_data(summaryLightDict,"sleep_Light", collection)
        
                    summaryRemDict = {
                        "dateTime": sleepItem['dateOfSleep'],
                        "value": sleepItem['levels']['summary']['rem']['minutes']
                    }
                    create_data(summaryRemDict,"sleep_Rem", collection)
        
                    summaryWakeDict = {
                        "dateTime": sleepItem['dateOfSleep'],
                        "value": sleepItem['levels']['summary']['wake']['minutes']
                    }
                    create_data(summaryWakeDict,"sleep_Wake", collection)
                else:
                    make_zero_sleep(base_date, end_date, collection)
                    continue
                
def getActivityData(base_date, end_date, token, collection):

    activityList = ['activities/minutesSedentary', 'activities/minutesLightlyActive','activities/minutesFairlyActive',
                    'activities/minutesVeryActive', 'activities/heart']
    
    minutesSedentary = df_fitbit(activityList[0], base_date, end_date, token)['activities-minutesSedentary']
    minutesLightlyActive = df_fitbit(activityList[1], base_date, end_date, token)['activities-minutesLightlyActive']
    minutesFairlyActive = df_fitbit(activityList[2], base_date, end_date, token)['activities-minutesFairlyActive']
    minutesVeryActive = df_fitbit(activityList[3], base_date, end_date, token)['activities-minutesVeryActive']
    heartRate = df_fitbit(activityList[4], base_date, end_date, token)['activities-heart']
    
    for sedentary in minutesSedentary:
        datetimeSed = sedentary['dateTime']
        totalTime = int(sedentary['value'])
        
        for heart in heartRate:
            if heart['dateTime'] == datetimeSed:
                if totalTime == 1440:
                    totalTime = 0
                minutesSedentaryDict = {
                    "dateTime": datetimeSed, 
                    "value": totalTime, 
                    } 
                create_data(minutesSedentaryDict,"minutesSedentary", collection)

                for lightlyActive in minutesLightlyActive:
                    if datetimeSed == lightlyActive['dateTime']:
                        minutesLightlyActiveDict = {
                            "dateTime": datetimeSed, 
                            "value": int(lightlyActive['value']), 
                            } 
                        create_data(minutesLightlyActiveDict,"minutesLightlyActive", collection)
                        totalTime += int(lightlyActive['value'])

                for fairlyActive in minutesFairlyActive:
                    if datetimeSed == fairlyActive['dateTime']:
                        minutesFairlyActiveDict = {
                            "dateTime": datetimeSed, 
                            "value": int(fairlyActive['value']), 
                            } 
                        create_data(minutesFairlyActiveDict,"minutesFairlyActive", collection)

                        totalTime += int(fairlyActive['value'])

                for veryActive in minutesVeryActive:
                    if datetimeSed == veryActive['dateTime']:
                        minutesVeryActiveDict = {
                            "dateTime": datetimeSed, 
                            "value": int(veryActive['value']), 
                            } 
                        create_data(minutesVeryActiveDict,"minutesVeryActive", collection)
                    
                        totalTime += int(veryActive['value'])
        activityDict = {
            "dateTime": datetimeSed, 
            "value": totalTime, 
            }    
    
        create_data(activityDict,"totalWearTime", collection)

def getStepsData(base_date, end_date, token, collection):
    steps_count_base = df_fitbit('activities/steps', base_date, end_date, token, intradays=True)
    steps_count_end = df_fitbit('activities/steps', end_date, base_date, token, intradays=True)

    # Create a dictionary for the steps count data for the current date
    stepsDictbase = {
        "dateTime": steps_count_base['activities-steps'][0]['dateTime'],
        "value": steps_count_base['activities-steps-intraday'].get('dataset', None), 
    }
    
    if not stepsDictbase:
        for h in range(9, 24):
            for m in range(0, 60, 15):
                time_str = '{:02d}:{:02d}:00'.format(h, m)
                stepsDictbase['value'].append({'time': time_str, 'value': 0})
        
    create_data(stepsDictbase, "stepsbase", collection)
    
    stepsDictend = {
        "dateTime": steps_count_end['activities-steps'][0]['dateTime'],
        "value": steps_count_end['activities-steps-intraday'].get('dataset', None), 
    }
    
    if not stepsDictend:
        for h in range(0, 10):
            for m in range(0, 60, 15):
                time_str = '{:02d}:{:02d}:00'.format(h, m)
                stepsDictend['value'].append({'time': time_str, 'value': 0})
                if h == 9 and m == 0:
                    break
    
    create_data(stepsDictend, "stepsend", collection)
    
def getCaloryData(base_date, end_date, token, collection):
    calroies_base = df_fitbit('activities/calories', base_date, end_date, token, intradays=True)
    calroies_end = df_fitbit('activities/calories', end_date, base_date, token, intradays=True)

    # Create a dictionary for the steps count data for the current date
    calroiesDictbase = {
        "dateTime": calroies_base['activities-calories'][0]['dateTime'],
        "value": calroies_base['activities-calories-intraday'].get('dataset', None), 
    }
    
    if not calroiesDictbase:
        for h in range(9, 24):
            for m in range(0, 60, 15):
                time_str = '{:02d}:{:02d}:00'.format(h, m)
                calroiesDictbase['value'].append({'time': time_str, 'value': 0})
        
    create_data(calroiesDictbase, "calroiesbase", collection)
    
    calroiesDictend = {
        "dateTime": calroies_end['activities-calories'][0]['dateTime'],
        "value": calroies_end['activities-calories-intraday'].get('dataset', None), 
    }
    
    if not calroiesDictend:
        for h in range(0, 10):
            for m in range(0, 60, 15):
                time_str = '{:02d}:{:02d}:00'.format(h, m)
                calroiesDictend['value'].append({'time': time_str, 'value': 0})
                if h == 9 and m == 0:
                    break
        
    create_data(calroiesDictend, "calroiesend", collection)

def getDistData(base_date, end_date, token, collection):
    dist_base = df_fitbit('activities/distance', base_date, end_date, token, intradays=True)
    dist_end = df_fitbit('activities/distance', end_date, base_date, token, intradays=True)

    # Create a dictionary for the steps count data for the current date
    distDictbase = {
        "dateTime": dist_base['activities-distance'][0]['dateTime'],
        "value": dist_base['activities-distance-intraday'].get('dataset', None), 
    }
    
    if not distDictbase:
        for h in range(9, 24):
            for m in range(0, 60, 15):
                time_str = '{:02d}:{:02d}:00'.format(h, m)
                distDictbase['value'].append({'time': time_str, 'value': 0})
        
    create_data(distDictbase, "distbase", collection)
    
    distDictend = {
        "dateTime": dist_end['activities-distance'][0]['dateTime'],
        "value": dist_end['activities-distance-intraday'].get('dataset', None), 
    }
    
    if not distDictend:
        for h in range(0, 10):
            for m in range(0, 60, 15):
                time_str = '{:02d}:{:02d}:00'.format(h, m)
                distDictend['value'].append({'time': time_str, 'value': 0})
                if h == 9 and m == 0:
                    break
        
    create_data(distDictend, "distend", collection)

def getHeartData(base_date, end_date, token, collection):
    heart_base = df_fitbit('activities/heart', base_date, end_date, token, intradays=True)
    heart_end = df_fitbit('activities/heart', end_date, base_date, token, intradays=True)

    # Create a dictionary for the steps count data for the current date
    heartDictbase = {
        "dateTime": heart_base['activities-heart'][0]['dateTime'],
        "value": heart_base['activities-heart-intraday'].get('dataset', None),
        "rest": heart_base['activities-heart'][0]['value'].get('restingHeartRate', None),
    }
    
    if not heartDictbase['value']:
        for h in range(9, 24):
            for m in range(0, 60, 15):
                time_str = '{:02d}:{:02d}:00'.format(h, m)
                heartDictbase['value'].append({'time': time_str, 'value': 0})
        
    
    if heartDictbase['rest'] is None:
        heartDictbase['rest'] = 0
        
    create_data(heartDictbase, "heartbase", collection)
    
    heartDictend = {
        "dateTime": heart_end['activities-heart'][0]['dateTime'],
        "value": heart_end['activities-heart-intraday'].get('dataset', None),
        "rest": heart_end['activities-heart'][0]['value'].get('restingHeartRate', None),
    }
    
    if not heartDictend['value']:
        for h in range(0, 10):
            for m in range(0, 60, 15):
                time_str = '{:02d}:{:02d}:00'.format(h, m)
                heartDictend['value'].append({'time': time_str, 'value': 0})
                if h == 9 and m == 0:
                    break
  
    if heartDictend['rest'] is None:
        heartDictend['rest'] = 0
        
    create_data(heartDictend, "heartend", collection)
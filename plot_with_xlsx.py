#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 10:58:10 2024

@author: jbc0102
"""
import warnings
warnings.filterwarnings(action='ignore')
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import utils as ut
import numpy as np

font_path = 'C:\WINDOWS\FONTS\MALGUN.TTF'
# font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
font_name=fm.FontProperties(fname=font_path).get_name()
plt.rc('font', family=font_name, size=12)
plt.rcParams['axes.unicode_minus'] = False

def convert_to_time_ratio(pct, all_values):
    total_time = sum(all_values)
    time_in_hours = total_time * (pct / 100)
    hours = int(time_in_hours)
    minutes = (time_in_hours - hours) * 60
    return f"{hours:02d}:{int(minutes):02d}"


def autopct_func(pct, df):
    total = df['value'].sum()
    value = pct * total / 100
    index = (df['value'] - value).abs().idxmin()
    return f'{df["hours_minutes"].loc[index]}'

def remove_none_value_rows(df):
    if len(df) >= 50 and 2.5 in df['level'].values:
        df = df[df['level'] != 2.5]
    return df   

def plot_sleep_stage(saved_data, ax):
    sleep_stage = saved_data[saved_data['type'] == 'sleep_stage']
    Stage = ut.get_df_columns(sleep_stage, False, False)
    df = Stage.explode('value')
    df['dateTime'] = pd.to_datetime(df['value'].apply(lambda x: x['dateTime']))
    df['second'] = df['value'].apply(lambda x: x['seconds'])
    df['end_time'] = df['dateTime'] + pd.to_timedelta(df['second'], unit='s')
    df['level'] = df['value'].apply(lambda x: x['level'])
    df.set_index('dateTime', inplace=True)
    df.drop(['value'], axis=1, inplace=True)
    level_mapping = {'deep': 1, 'light': 2, 'rem': 3, 'wake': 4, 'none': 2.5}
    df['level'] = df['level'].map(level_mapping)
    df.dropna(inplace=True)
    df = remove_none_value_rows(df)

    ax.plot([], [])
    
    for index, row in df.iterrows():
        level = row['level']
        color = np.array([0, 0, 0.53]) if level == 1 else \
            np.array([0, 0, 0.98]) if level == 2 else \
            np.array([0, 0.54, 0.78]) if level == 3 else np.array([1, 0, 0])
            
        if index < df.index[-1]:
            next_index_time = df.index[df.index.get_loc(index) + 1]
            next_level = df.loc[next_index_time, 'level']
            ax.plot([row['end_time'], next_index_time], [level, next_level], color=(0,0,0, 0.3), linewidth=2.5, solid_capstyle='round')
        ax.plot([index, row['end_time']], [level, level], label=level, color=color, linewidth=3, solid_capstyle='round')
            # , fontproperties=font_prop
    ax.set_title('시간 별 수면 상태')
    ax.set_yticks(range(1, 5), ['깊은', '얕은', '램', '기상'])
    hourly_ticks = pd.date_range(start=df.index.min(), end=df.index.max() + pd.DateOffset(hours=1), freq='1H')
    ax.set_xticks(hourly_ticks, [time.strftime('%H') for time in hourly_ticks])
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

def remove_zero_value_rows(df):
    if len(df) >= 2 and 0 in df['value'].values:
        df = df[df['value'] != 0]
    return df   

def plot_sleep_time(saved_data, ax):
    # Time_bed = saved_data[saved_data['type'] == 'timeInBed']
    # bed_duration = ut.get_minutes_in_hour_minutes(Time_bed)['hours_minutes'][0]

    sleep_duration = saved_data[saved_data['type'] == 'minutesAsleep']
    duration = ut.get_minutes_in_hour_minutes(sleep_duration)
    duration = remove_zero_value_rows(duration)['hours_minutes'][0]

    sleep_Deep = saved_data[saved_data['type'] == 'sleep_Deep']
    deep_sleep = ut.get_minutes_in_hour_minutes(sleep_Deep)
    deep_sleep = remove_zero_value_rows(deep_sleep)

    sleep_Light = saved_data[saved_data['type'] == 'sleep_Light']
    light_sleep = ut.get_minutes_in_hour_minutes(sleep_Light)
    light_sleep = remove_zero_value_rows(light_sleep)

    sleep_Rem = saved_data[saved_data['type'] == 'sleep_Rem']
    rem_sleep = ut.get_minutes_in_hour_minutes(sleep_Rem)
    rem_sleep = remove_zero_value_rows(rem_sleep)

    sleep_Wake = saved_data[saved_data['type'] == 'sleep_Wake']
    wake_sleep = ut.get_minutes_in_hour_minutes(sleep_Wake)
    wake_sleep = remove_zero_value_rows(wake_sleep)

    df_merged = pd.concat([deep_sleep, light_sleep, rem_sleep], keys=['깊은', '얕은', '램'])
    if df_merged['value'].sum() == 0:
        df_merged['value'] = 8
        df_merged['hours_minutes'] = '00h 00m'

    explode = [0.05, 0.05, 0.05]
    
    ax.plot([], [])

    ax.pie(df_merged['value'], labels=df_merged.index.get_level_values(0), startangle=140, autopct=lambda pct: autopct_func(pct, df_merged),
            pctdistance=0.5, explode=explode, shadow=True)
    ax.set_title('수면 상태 별 시간')
    ax.text(-2, -1.4, '수면 시간    = {}'.format(duration))
    ax.text(-2, -1.7, '깨어난 시간 = {}'.format(wake_sleep['hours_minutes'].iloc[0]))

    
def plot_step_heart_time(saved_data, ax):
    step_base = saved_data[saved_data['type'] == 'stepsbase']
    step_end = saved_data[saved_data['type'] == 'stepsend']

    df_step = ut.one_intradays(step_base, step_end)
    
    heart_base = saved_data[saved_data['type'] == 'heartbase']
    heart_end = saved_data[saved_data['type'] == 'heartend']

    df_heart = ut.one_intradays(heart_base, heart_end, True)
    rest_heart = round(df_heart['rest'].mean())
    
    ax.plot([], [])
    ax.bar(df_step.index, df_step['value'], width=0.009, color='orange', alpha=0.5)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.tick_params('y', colors='orange')
    ax.set_ylabel('걸음 수')
        
    ax1 = ax.twinx()
    ax1.plot(df_heart['value'], color='r', marker='o')
    ax1.tick_params('y', colors='r')
    ax1.set_ylabel('심박수 (BPM)')
    ax1.spines['left'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    hourly_ticks = pd.date_range(start=df_heart.index.min(), end=df_heart.index.max(), freq='2H')
    ax.set_xticks(hourly_ticks, [time.strftime('%H') for time in hourly_ticks])
        
    ax.set_title('시간별 걸음 수 (주황) 및 심박수 (빨강), 안정시 심박수 = {} BPM'.format(rest_heart))

def plot_step_time(saved_data, ax):
    step_base = saved_data[saved_data['type'] == 'stepsbase']
    step_end = saved_data[saved_data['type'] == 'stepsend']

    df_result = ut.one_intradays(step_base, step_end)

    ax.plot([], [])
    ax.bar(df_result.index, df_result['value'], width=0.009, color='orange')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    hourly_ticks = pd.date_range(start=df_result.index.min(), end=df_result.index.max(), freq='2H')
    ax.set_xticks(hourly_ticks, [time.strftime('%H') for time in hourly_ticks])
    ax.set_title('시간별 걸음 수')

def plot_heart_time(saved_data, ax):
    heart_base = saved_data[saved_data['type'] == 'heartbase']
    heart_end = saved_data[saved_data['type'] == 'heartend']

    df_result = ut.one_intradays(heart_base, heart_end, True)
    rest_heart = round(df_result['rest'].mean())

    ax.plot([], [])
    ax.plot(df_result['value'], color='r', marker='o')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    hourly_ticks = pd.date_range(start=df_result.index.min(), end=df_result.index.max(), freq='2H')
    ax.set_xticks(hourly_ticks, [time.strftime('%H') for time in hourly_ticks])
    ax.set_title('시간별 심박수, 안정시 심박수 = {} BPM'.format(rest_heart))

def plot_whole_days(saved_data, ax):
    step_base = saved_data[saved_data['type'] == 'stepsbase']
    step_end = saved_data[saved_data['type'] == 'stepsend']
    
    df_step = ut.one_intradays(step_base, step_end)
    
    whole_step = df_step['value'].sum()
    
    cal_base = saved_data[saved_data['type'] == 'calroiesbase']
    cal_end = saved_data[saved_data['type'] == 'calroiesend']
    
    df_cal = ut.one_intradays(cal_base, cal_end)
    
    whole_cal = round(df_cal['value'].sum())
    
    dist_base = saved_data[saved_data['type'] == 'distbase']
    dist_end = saved_data[saved_data['type'] == 'distend']
    
    df_dist = ut.one_intradays(dist_base, dist_end)
    
    whole_dist = round(df_dist['value'].sum(), 2)
    
    image_path = './Icons/steps.png' # "https://icons8.com/icon/zdvjS4pTUz1Q/baby-footprint"
    imagebox = OffsetImage(plt.imread(image_path), zoom=1.2)
    ab = AnnotationBbox(imagebox, (0.3, 0.9), frameon=False)
    ax.add_artist(ab)
    ax.text(0.04, 0.76, '{:5,} 걸음'.format(whole_step))
    
    image_path = './Icons/calories.png' # "https://icons8.com/icon/qgI0bh6LyBai/metabolism"
    imagebox = OffsetImage(plt.imread(image_path), zoom=0.9)
    ab = AnnotationBbox(imagebox, (0.3, 0.55), frameon=False)
    
    ax.add_artist(ab)
    ax.text(0.04, 0.4, '{:5,} 칼로리'.format(whole_cal))
    
    image_path = './Icons/distance.png' #"https://icons8.com/icon/48400/place-marker"
    imagebox = OffsetImage(plt.imread(image_path), zoom=1)
    ab = AnnotationBbox(imagebox, (0.3, 0.2), frameon=False)
    ax.add_artist(ab)
    ax.text(0.07, 0.05, '{:4,} KM'.format(whole_dist))
    
    ax.set_title('총 활동량          ')
    
    ax.axis('off')

def plot_user_activity(saved_data, ax):
    minutesSedentary_df, minutesLightlyActive_df, minutesFairlyActive_df, minutesVeryActive_df = ut.get_activity_value(saved_data)

    sedentary_time = minutesSedentary_df.sum()['minutesSedentary']
    lightly_active_time = minutesLightlyActive_df.sum()['minutesLightlyActive']
    fairly_active_time = minutesFairlyActive_df.sum()['minutesFairlyActive']
    very_active_time = minutesVeryActive_df.sum()['minutesVeryActive']
    
    labels = ['정적', '보통', '약간', '매우']
    sizes = [sedentary_time, fairly_active_time, lightly_active_time, very_active_time]
    non_zero_sizes = [size for size, label in zip(sizes, labels) if size != 0]
    non_zero_labels = [label for size, label in zip(sizes, labels) if size != 0]
           
    ax.bar(non_zero_labels, non_zero_sizes, color='coral')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.set_title('활동량 별 시간 (분)')

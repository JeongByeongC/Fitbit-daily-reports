#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 13:52:23 2024

@author: jbc0102
"""

from ExportWebAPI import getSleepData, getActivityData, getStepsData, getCaloryData, getDistData, getHeartData
from token_utils import automate_code_retrieval, automate_token_retrieval
import utils as ut
from plot_with_xlsx import plot_sleep_stage, plot_sleep_time, plot_user_activity, plot_step_heart_time, plot_whole_days
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from selenium.webdriver.chrome.options import Options
from datetime import timedelta
import os
import time

import tkinter as tk
from tkcalendar import DateEntry
from babel.numbers import *
from tkinter import filedialog, messagebox, ttk

#ID list removed 
ID_list = []

def select_all():
    username_listbox.select_set(0, tk.END)
    
def update_progressbar(value):
    progress_bar['value'] = value
    root.update_idletasks()

def print_information():
    global selected_usernames, BASE_DATE, END_DATE, folder_selected
    selected_usernames = username_listbox.curselection()
    if not selected_usernames:
        messagebox.showinfo("알림", "계정을 선택하세요.")
        return

    
    FITBIT_USERNAMES = [ID_list[i] for i in selected_usernames]
    FITBIT_PASSWORDS = [f"{username[6:]}{username[:6]}!" if username[6:] in ['030', '037'] else f"{username[6:]}{username[:6]}@guro" if username[6:] in ['055', '056'] else f"{username[6:]}{username[:6]}@" for username in FITBIT_USERNAMES]
    END_DATE = date_entry.get_date()
    BASE_DATE = END_DATE - timedelta(days=1)
    folder_selected = filedialog.askdirectory()

    output_text.delete(1.0, tk.END)

    for idx, username in enumerate(FITBIT_USERNAMES):
        file_path = f"{folder_selected}/{username}_{END_DATE}.pdf"
        collection_path = f"{folder_selected}/{username}_{END_DATE}.xlsx"
        output_text.insert(tk.END, f"FITBIT 계정 {idx + 1}: {username}\n")
        output_text.insert(tk.END, f"FITBIT 비밀번호 {idx + 1}: {FITBIT_PASSWORDS[idx]}\n")
        output_text.insert(tk.END, f"PDF 저장 경로 {idx + 1}: {file_path}\n")
        output_text.insert(tk.END, f"EXCEL 저장 경로 {idx + 1}: {collection_path}\n")
    output_text.insert(tk.END, f"데이터 추출 날짜: {BASE_DATE} ~ {END_DATE}\n")

def call_save_pdf(file_path, collection, BASE_DATE, END_DATE):
    a4_width = 210
    a4_height = 297
    figsize=(a4_height/25.4, a4_width/25.4)
    num_rows = 6
    num_cols = 8
    fig = plt.figure(figsize=figsize)
    gs = plt.GridSpec(num_rows, num_cols, wspace=2, hspace=1.2)

    plt.suptitle('{} 오전 9시 ~ {} 오전 9시 활동 내역'.format(BASE_DATE, END_DATE))

    ax0 = plt.subplot(gs[0:4, 0:2])
    ax1 = plt.subplot(gs[0:4, 2:])
    ax2 = plt.subplot(gs[4:, 0:2])
    ax3 = plt.subplot(gs[4:, 2:])


    plot_whole_days(collection, ax0)

    plot_step_heart_time(collection, ax1)
    ax1.spines['left'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    plot_sleep_time(collection, ax2)

    plot_sleep_stage(collection, ax3)

    plt.tight_layout()
    plt.savefig('{}'.format(file_path), bbox_inches='tight', pad_inches=0)
    plt.close(fig)

def save_pdf():
    global selected_usernames, BASE_DATE, END_DATE, folder_selected
    if not selected_usernames:
        messagebox.showinfo("알림", "계정을 선택하세요.")
        return

    FITBIT_CLIENT_ID = '238Y2L'
    FITBIT_CLIENT_SECRET = '2fa3dd149aac30def38f029e05368bf1'

    for idx in selected_usernames:
        progress_bar['value'] = 0
        username = ID_list[idx]
        file_path = f"{folder_selected}/{username}_{END_DATE}.pdf"
        collection_path = f"{folder_selected}/{username}_{END_DATE}.xlsx"

        if os.path.isfile(collection_path):
            output_text.insert(tk.END, f"로컬에 저장된 정보로부터 PDF를 저장합니다. ({username})\n")
        else:
            output_text.insert(tk.END, f"FITBIT 서버로부터 데이터를 로컬에 저장하고 PDF를 저장합니다. ({username})\n")
            chrome_options = Options()
            # chrome_options.add_argument('--disable-gpu')
            
            id_ = f"{username}@naver.com" if username[6:] in ['062'] else f"{username}@gmail.com"
            passward = f"{username[6:]}{username[:6]}!" if username[6:] in ['030', '037'] else f"{username[6:]}{username[:6]}@guro" if username[6:] in ['055', '056'] else f"{username[6:]}{username[:6]}@"
            code = automate_code_retrieval(id_, passward, FITBIT_CLIENT_ID, chrome_options)
            token = automate_token_retrieval(code, FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET)
            try:
                time.sleep(5)
                getSleepData(BASE_DATE, END_DATE, token, collection_path)
                getActivityData(BASE_DATE, END_DATE, token, collection_path)
                getStepsData(BASE_DATE, END_DATE, token, collection_path)
                getCaloryData(BASE_DATE, END_DATE, token, collection_path)
                getDistData(BASE_DATE, END_DATE, token, collection_path)
                getHeartData(BASE_DATE, END_DATE, token, collection_path)
            except Exception as e:
                output_text.insert(tk.END, f"데이터가 없어서 PDF 생성이 실패했습니다. ({username})\n")
                output_text.insert(tk.END, f"에러 메시지: {str(e)}\n")
                continue

        try:
            collection = ut.load_data(collection_path)
            call_save_pdf(file_path, collection, BASE_DATE, END_DATE)
            output_text.insert(tk.END, f"PDF 생성이 완료되었습니다. ({username})\n")
        except Exception as e:
            output_text.insert(tk.END, f"데이터 로드 중 오류가 발생하여 PDF 생성이 실패했습니다. ({username})\n")
            output_text.insert(tk.END, f"에러 메시지: {str(e)}\n")
        
        update_progressbar((idx + 1) / len(selected_usernames) * 100)
    



root = tk.Tk()
root.title("FITBIT 정보 입력")
root.geometry("900x900")

selected_usernames = []
BASE_DATE = ""
folder_selected = ""

# Fitbit ID removed
FITBIT_USERNAMES = []

username_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, font=("Helvetica", 14), height=18)
username_listbox.grid(row=0, column=0, padx=10)

for username in FITBIT_USERNAMES:
    username_listbox.insert(tk.END, username)

select_all_button = tk.Button(root, text="모두 선택", command=select_all, font=("Helvetica", 14, 'bold'), height=18)
select_all_button.grid(row=0, column=1, sticky='n', pady=10)

date_label = tk.Label(root, text="기준 날짜:", font=("Helvetica", 14, 'bold'))
date_label.grid(row=0, column=2, sticky='nesw', padx=10)

date_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2, font=("Helvetica", 14))
date_entry.grid(row=0, column=3, padx=10)

print_button = tk.Button(root, text="정보 출력", command=print_information, font=("Helvetica", 14, 'bold'), width=15)
print_button.grid(row=0, column=2, columnspan=2,sticky='s')

pdf_button = tk.Button(root, text="PDF 생성", command=save_pdf, font=("Helvetica", 14, 'bold'), width=15)
pdf_button.grid(row=0, column=4, columnspan=2,sticky='s')

progress_bar = ttk.Progressbar(root, orient="horizontal", length=870, mode="determinate")
progress_bar.grid(row=1, column=0, columnspan=5, sticky='nesw', padx=15)

output_text = tk.Text(root, height=30, width=70, font=("Helvetica", 14))
output_text.grid(row=2, column=0, columnspan=5, sticky='nesw', padx=15)

output_text.tag_configure('bold', font=('Helvetica', 14, 'bold'))

root.mainloop()

# Fitbit daily reports

## Overview

The Fitbit daily reports project automates the processing and visualizaion of Fitbit data. This project is designed to complement a program installed in hospital wards, where Fitbit devices are configured to disable screen output to prevent patients from viewing real-time feedback [Fitbit Real-Time](https://github.com/JeongByeongC/Fitbit-Real-Time). The purpose of this project is to generate comprehensive daily reports based on Fitbit data, which can be shared with patients to encourage consistent Fitbit usage. If you want to see demo video click [here](#Deme-Video).

## Features

  + **User-Friendly GUI**: Provides a user-friendly graphical intercace for easy interaction.

  + **Selective Data Extraction**: Allows users to extract data only from specific Fitbit devices as needed.

  + **Custom Date Selection**: Enables users to generate reports fro speccific dates by chaging the date range.
  
  +  **Date Export**: Automates data export from Fitbit server using provieded APIs.

  + **Data Visualization**: Creates figures from Fitbit data stored in excel files.

## File Descriptions

  + **ExpeortWebAPI.py**: Handles exporting Fitbit data through the Fitbit Web API.

  + **plot_with_xlsx.py**: Generates visualizations from Fitbit data stored in Excel files.

  + **save_fitbit_data_PDF.py**: Converts processed Fitbit data into formatted PDF reports.

  + **token_utils.py**: Contains helper functions to manage APU tokens securely.

  + **utils.py**: General utility functions for data handling and formatting.

## Prerequisites

Ensure you have the following installed:

  + Python 3.7 or higher

  + Required Python libraries (see below)

    + Babel==2.11.0
   
    + matplotlib==3.5.3
   
    + numpy==1.21.5
   
    + pandas==1.3.5
   
    + Requests==2.32.3
   
    + selenium==4.28.1
   
    + tkcalendar==1.6.1
   
    + undetected_chromedriver==3.5.5
   
    + webdriver_manager==4.0.2
   
    + or
      ```
      pip install -r requirements.txt
      ```

  + Google Chorme version 121.0.6167.185 (Official Build, 64-bit) necessary for Selenium

## Usage

You can use the project in two ways:

1. **Run Python Scripts**: Execute the provided Python scripts directly to generate daily PDF reports. For example:

```
python save_fitbit_data_PDF.py
```

2. **Create and Run Executable Files**: If you prefer ont to run Python scripts directly, you can create standalone excutable files using tooks like **pyinstaller**:

```
pyinstaller --onefile save_fitbit_data_PDF.py --hidden-import openpyxl.cell._writer
```

  + **Windows**: Executable files created on Windows can only be run on Windows.

  + **macOS**: If you need an executable for macOS, you must create it on a macOS machine.

Once the executavle is created, simply run it by double cliking the excutable file in the dist folder.

## Deme Video
![Image](https://github.com/user-attachments/assets/d9c40455-ef4d-46b1-9d9d-b38549a355c9)

import pandas as pd
from shiny import reactive
from pathlib import Path


"""
The load_data file contains the instructions to load csv files and save them into datagrames.
The dataframes are then imported in the main app.
"""
app_dir = Path(__file__).parent

DATA_DIR = app_dir / 'data'
DATA_FILE = app_dir / 'data' /'database.xlsx'

## TO DO
## func: retrieve data from db or csv
## func: put data into a dataframe and return the df
## func: save edited data from df to csv/db

def import_calendar():
    try:
        ## import from csv to df
        data = pd.read_csv(DATA_DIR / 'calendar.csv')
        ## convert dates to datetime
        data['start_date'] = pd.to_datetime(data.start_date, dayfirst=True, errors='raise', format='mixed')
        data['end_date'] = pd.to_datetime(data.end_date, dayfirst=True, errors='raise', format='mixed')
        ## if remarks is nan it creates an error when plotting (cannot create JSON object from nan)
        data['remarks'] = data.remarks.fillna(0)
        return data
    except Exception as e:
        print(f'Oops, something went wrong\nException: {e}')
        return None

def update_calendar(data):
    file = DATA_DIR / 'calendar.csv'
    data.to_csv(file, mode='w', index=False, header=True)

def add_cal_row(new_row):
    cal_cols = ['advisor', 'start_date', 'end_date', 'type', 'remarks']
    ## make sure the new dataframe has the correct order of columns
    new_row = new_row.reindex(columns=cal_cols)
    ## convert dates to datetime
    new_row['start_date'] = pd.to_datetime(new_row.start_date, dayfirst=True, errors='raise', format='mixed')
    new_row['end_date'] = pd.to_datetime(new_row.end_date, dayfirst=True, errors='raise', format='mixed')

    file = DATA_DIR / 'calendar.csv'

    if not file.exists():
        new_row.to_csv(file, mode='a', index=False, header=True)
    else:
        new_row.to_csv(file, mode='a', index=False, header=False)


advisors = pd.read_excel(DATA_FILE, sheet_name='advisors')
wash_list = pd.read_excel(DATA_FILE, sheet_name='wash_list')
countries = pd.read_excel(DATA_FILE, sheet_name='countries')
# calendar = pd.read_excel(DATA_FILE, sheet_name='calendar')

# ## Import the calendar table
# calendar = pd.read_csv(DATA_DIR / 'calendar.csv')
# ## convert the date columns to datetime
# try:
#     calendar['start_date'] = pd.to_datetime(calendar.start_date, dayfirst=True, errors='raise', format='mixed')
#     calendar['end_date'] = pd.to_datetime(calendar.end_date, dayfirst=True, errors='raise', format='mixed')
# except Exception as e:
#     print(f'Error: {e}')
# ## if remarks is nan it creates an error when plotting (cannot create JSON object from nan)
# calendar['remarks'] = calendar.remarks.fillna(' ')

## Use reactive value to rewrite the calendar data import
calendar = reactive.Value()
data = pd.read_csv(DATA_DIR / 'calendar.csv')
## convert the date columns to datetime
try:
    data['start_date'] = pd.to_datetime(data.start_date, dayfirst=True, errors='raise', format='mixed')
    data['end_date'] = pd.to_datetime(data.end_date, dayfirst=True, errors='raise', format='mixed')
except Exception as e:
    print(f'Error: {e}')
## if remarks is nan it creates an error when plotting (cannot create JSON object from nan)
data['remarks'] = data.remarks.fillna(' ')
## store the dataframe into the reactive variable
calendar.set(data)
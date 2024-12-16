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


advisors = pd.read_excel(DATA_FILE, sheet_name='advisors')
wash_list = pd.read_excel(DATA_FILE, sheet_name='wash_list')
countries = pd.read_excel(DATA_FILE, sheet_name='countries')
# calendar = pd.read_excel(DATA_FILE, sheet_name='calendar')

## Import the calendar table
calendar = pd.read_csv(DATA_DIR / 'calendar.csv')
## convert the date columns to datetime
try:
    calendar['start_date'] = pd.to_datetime(calendar.start_date, dayfirst=True, errors='raise', format='mixed')
    calendar['end_date'] = pd.to_datetime(calendar.end_date, dayfirst=True, errors='raise', format='mixed')
except Exception as e:
    print(f'Error: {e}')
## if remarks is nan it creates an error when plotting (cannot create JSON object from nan)
calendar['remarks'] = calendar.remarks.fillna(' ')
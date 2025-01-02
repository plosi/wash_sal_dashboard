from shiny import ui, reactive
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

### LOADING DATA ###
"""
The load_data file contains the instructions to load csv files and save them into datagrames.
The dataframes are then imported in the main app.

TO DO
func: retrieve data from db or csv
func: put data into a dataframe and return the df
func: save edited data from df to csv/db

"""

app_dir = Path(__file__).parent

# DATA_DIR = app_dir / 'data'
DATA_FILE = app_dir / 'data' / 'database.xlsx'

ADVISOR_PALETTE = ['#ef476f', '#ffd166', '#06d6a0', '#118ab2']
TYPE_PALETTE = ['#ffd300', '#ff0000', '#ff0000', '#d11149', '#ff0000', '#d11149', '#04e762', '#008bf8', '#e5e5e5']
# types = ['Country Support Visit','Bank Holiday','Leave Full Day','Leave Half Day','Time In Lieu Full Day','Time In Lieu Half Day','Conference/Workshop','Training','Personal Commitment (no travel)']

advisors = pd.read_excel(DATA_FILE, sheet_name='advisors')
countries = pd.read_excel(DATA_FILE, sheet_name='countries')
# wash_list = pd.read_excel(DATA_FILE, sheet_name='wash_list')
# calendar = pd.read_excel(DATA_FILE, sheet_name='calendar')
types = pd.read_excel(DATA_FILE, sheet_name='types').type.to_list()

def import_calendar():
    try:
        ## import from excel
        data = pd.read_excel(DATA_FILE, sheet_name='calendar')
        ## convert dates to datetime
        data['start_date'] = pd.to_datetime(data.start_date, dayfirst=True, errors='raise', format='%d-%b-%Y')#'mixed')
        data['end_date'] = pd.to_datetime(data.end_date, dayfirst=True, errors='raise', format='%d-%b-%Y')#'mixed')
        return data
    except Exception as e:
        print(f'Oops, something went wrong\nException: {e}')
        return None

def update_calendar(data):
    ## if there's a column named id, drop it
    if 'id' in data.columns:
        data = data.drop('id', axis=1)
    ## replace the calendar sheet in the excel file
    with pd.ExcelWriter(DATA_FILE, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        data.to_excel(writer, 'calendar', index=False)

def import_country_calls():
    try:
        data = pd.read_excel(DATA_FILE, sheet_name='country_calls')
        return data
    except Exception as e:
        print(f'Oops, something went wrong: {e}')
        return None

def update_country_calls(data):
    ## if there's a column named id, drop it
    if 'id' in data.columns:
        data = data.drop('id', axis=1)
    ## replace the calendar sheet in the excel file
    with pd.ExcelWriter(DATA_FILE, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        data.to_excel(writer, 'country_calls', index=False)

def import_wash_list():
    try:
        ## import from excel
        data = pd.read_excel(DATA_FILE, sheet_name='wash_list')
        return data
    except Exception as e:
        print(f'Oops, something went wrong\nException: {e}')
        return None

## CALENDAR FUNCTIONS ##
# advisors = import_advisors()

def pcg_days_by_type(data, year):
    def total_busdays(data):
        ## calculate the number of business days between two dates
        return len(pd.bdate_range(data.start_date, data.end_date))
    
    data['total_busdays'] = data.apply(total_busdays, axis=1)
    ## count how many days each advisor spent during the year by type 
    data_grouped = data[data.end_date.dt.year == year].groupby(['advisor', 'type']).agg({'total_busdays':'sum'}).reset_index()
    yr_busdays = np.busday_count(str(year), str(year+1))
    data_grouped['pcg_busdays'] = (data_grouped.total_busdays / yr_busdays)*100

    return data_grouped

### UI FUNCTIONS ###

def date_prettify(series):
    return f'{series:%d-%b-%Y}'


ADD_CALENDAR = {
    'advisor': ui.input_select(
        id='add_advisor',
        label='',
        ## create a dictionary with keys = advisor name
        choices={k:k for k in advisors.short_name.sort_values()}
    ),
    'type': ui.input_radio_buttons(
        id='add_type',
        label='',
        choices=types
    ),
    'start_date': ui.input_date(
        id='add_start_date',
        label='From:',
        value=datetime.today(),
        format='dd-mm-yyyy',
        min='2024-01-01',
        max=datetime.today() + timedelta(weeks=52)
    ),
    'end_date': ui.input_date(
        id='add_end_date',
        label='To:',
        value=datetime.today(),
        format='dd-mm-yyyy',
        min='2024-01-01',
        max=datetime.today() + timedelta(weeks=52)
    ),
    'remarks': ui.input_text(
        id='add_remarks',
        label='Description',
        placeholder='e.g. country name '
    )
}

EDIT_CALENDAR = {
    'advisor': ui.input_select(
        id='edit_advisor',
        label='',
        ## create a dictionary with keys = advisor name
        choices={k:k for k in advisors.short_name.sort_values()}
    ),
    'type': ui.input_radio_buttons(
        id='edit_type',
        label='',
        choices=types
    ),
    'start_date': ui.input_date(
        id='edit_start_date',
        label='From:',
        value=datetime.today(),
        format='dd-mm-yyyy',
        min='2024-01-01',
        max=datetime.today() + timedelta(weeks=52)
    ),
    'end_date': ui.input_date(
        id='edit_end_date',
        label='To:',
        value=datetime.today(),
        format='dd-mm-yyyy',
        min='2024-01-01',
        max=datetime.today() + timedelta(weeks=52)
    ),
    'remarks': ui.input_text(
        id='edit_remarks',
        label='Description',
        placeholder='e.g. country name '
    )
}

countries_list = countries['CIA Name'].to_list()
countries_list.append('Hanaano')
ADD_CALL = {
    'date': ui.input_date(
        id='add_date_call',
        label='Date:',
        value=datetime.today(),
        format='dd-mm-yyyy',
        min='2024-01-01',
        max=datetime.today() + timedelta(weeks=52)
    ),
    'country': ui.input_select(
        id='add_country_call',
        label='',
        ## create a dictionary with keys = country names
        # choices={k:k for k in countries['CIA Name'].sort_values()}
        choices={k:k for k in sorted(countries_list)}
    ),
    'sal_attendees': ui.input_text(
        id='add_sal_attendees_call',
        label='SAL TA',
        placeholder='comma separated names'
    ),
    'country_attendees': ui.input_text(
        id='add_country_attendees_call',
        label='Country Attendee(s)',
        placeholder='comma separated names'
    ),
    'description': ui.input_text_area(
        id='add_description_call',
        label='Description',
        placeholder='e.g., monthly catch-up',
        width='400px',
        height='200px'
    )
}

EDIT_CALL = {
    'date': ui.input_date(
        id='edit_date_call',
        label='Date:',
        value=datetime.today(),
        format='dd-mm-yyyy',
        min='2024-01-01',
        max=datetime.today() + timedelta(weeks=52)
    ),
    'country': ui.input_select(
        id='edit_country_call',
        label='',
        ## create a dictionary with keys = country names
        # choices={k:k for k in countries['CIA Name'].sort_values()}
        choices={k:k for k in sorted(countries_list)}
    ),
    'sal_attendees': ui.input_text(
        id='edit_sal_attendees_call',
        label='SAL TA',
        placeholder='comma separated names'
    ),
    'country_attendees': ui.input_text(
        id='edit_country_attendees_call',
        label='Country Attendee(s)',
        placeholder='comma separated names'
    ),
    'description': ui.input_text_area(
        id='edit_description_call',
        label='Description',
        placeholder='e.g., monthly catch-up',
        width='400px',
        height='200px'
    )
}
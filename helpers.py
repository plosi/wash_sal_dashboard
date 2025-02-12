from shiny import ui, reactive
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import os

import gspread
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from google.oauth2.service_account import Credentials

# from crud_helpers import CRUDHelper

### Colour palettes
ADVISOR_PALETTE = ['#ef476f', '#ffd166', '#FF8A8A', '#118ab2', '#06d6a0']
TYPE_PALETTE = ['#ffd300', '#ff0000', '#ff0000', '#d11149', '#ff0000', '#d11149', '#04e762', '#008bf8', '#403e3e']

### LOADING DATA ###
url = 'https://docs.google.com/spreadsheets/d/1xn5z6przqQh-jkVt32wXYYu48mgHz9RAD_8BQwAnkEo/edit?usp=sharing'
app_dir = Path(__file__).parent
GS_KEY = app_dir / 'gs_config.json'
GS_FILE_ID = '1xn5z6przqQh-jkVt32wXYYu48mgHz9RAD_8BQwAnkEo'

def initialize_gspread():
    """Initialize gspread with service account credentials."""

    ## If running locally with the config file...
    if os.path.isfile(GS_KEY):
        ## Define the scope
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]

        try:
            # Load credentials from service account file
            credentials = Credentials.from_service_account_file(
                GS_KEY,
                scopes=scope
            )
            # Authenticate and create client
            return gspread.authorize(credentials)
        except FileNotFoundError:
            credentials = {
                "type": "service_account",
                "project_id": "cww-wash-dashboard",
                "private_key_id": str(os.getenv('private_key_id')),
                "private_key": str(os.getenv('private_key')),
                "client_email": "cww-wash-dashboard-shiny-app@cww-wash-dashboard.iam.gserviceaccount.com",
                "client_id": "103153184028709897384",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/cww-wash-dashboard-shiny-app%40cww-wash-dashboard.iam.gserviceaccount.com",
                "universe_domain": "googleapis.com"
            }
            # Authenticate from dictionary
            return gspread.service_account_from_dict(credentials)

    credentials = {
            "type": "service_account",
            "project_id": "cww-wash-dashboard",
            "private_key_id": os.getenv('PRIVATE_KEY_ID'),
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDfudpjqeJZtx+H\nX1kNqnCz0RPwGYoA1NiI77QG+GOZMHarxW/+YxwgLJFvdJuQWTDa/MrsQgfj7tlg\n2KjFYr4iKsNkIK9LUC1GlIBKS3KBcxO3XGwV2c5VtA6YUhdNhA1P5JWQDcLMSnfl\nFFFfsX/LixYFhqXh4k56PX0UAFFCZtz74hZXJDxhrKFnWxdF6n4Un52tq5xZT07o\ntfbZuYXzlmbHC0bq2+A4oRv3ev3/I5CaIexwaQun/bI2elvI02yEl9ejFNCfxWCJ\nNg3M/P1LDEpuKuncMI95hH1C6tMVsxsqvxAYxuRGtWRfuOcwSfAPurRx+PrzQkM2\ntOovIsThAgMBAAECggEAAhq2/BhgSpqdSV4/ScCOWTOkj83msVevLnkOOQFPuwR0\nnkyf7z0uidsvdkRbFPxQyEOH01ly5m0EBowdKMejLRI4xqWjznYbaeo6S3Cam+75\nmtA7zEgRX7cfCsXdZh9RinyGf12QxTAHYQxMEGXMk10cXLqRr35r4WyYA0bWPNUT\nOiFQWoRuXS0vz6E9guYJIJgbThdb5rf1U/vw3VkeOtXNfZ+8n/LPP5NagliFI4wR\nbK2TcD9rjCqZwLQ8VvRnK/bLpMJgpmj+Ul+LhPlDHK7NVb+23K7tO5BRizsMnJGI\nZ0V4GgCnP5PXlZadOaBGGsWZRP6VOwDxB4QDIMslAQKBgQD5ex88PwAhlqEdf9fy\nzBQWMlwZu2r3TfPlZN/dhA0JllCTvGNgwmuEF1Pxb0KG+IPoXrnKIiHo9vbfCoR6\nfovAzeIj42JizvLN2ZnDMQiz1TEhuz/qnRAMp2ilE1urMeAt9bZC0RlIjL/JLr/6\nFIa5ED1JB61kXB/f5wz6bmfYgQKBgQDlknIjBZGBP0DIApauKiJknIcX/h+8czY5\ncXOvreDHp6yGbNrtolPh+pXVIiAFapIRdShj/qcnBCB6BHyfkcPDi1NdFhgpHx92\nAi29P049SLqhFfGsabQ7tNXmwJy+g2QOVHe2AnPbU1hnYwlAe1uBG7J0pIXlGJTP\n+qJZKUu8YQKBgCQZX7Ss/QzfKeMF266DPyjTEqaaiujL+82mogoAkI5hlLk72jln\nCH2tjnTx/3NeRF/8TO/lrnhyO9icQf0jkH9OizlcLqFThqioououjy7OW3ShDqeZ\nIHhkRO0V9v63kdO0qTHT5c+spherTxYVoETpB6UomjtaZTZVzXfzP82BAoGAPtUL\nGhy/C0HVqChVN0ve5+yTaPSrmPdrguNTR2TunZZ9uLj4XovMK5BbC99wJitZ2R9Y\ns62R8DLH9L1foojRrKZoZZTTfgW/pZvJCv/VmR5bvhT0dTzlEGZZGPPkspvhea6S\nqSUYspGoI3vOn3Bjxf1fpV8WKnLE3/t4DbEowmECgYEAz4oDcsrXpcg4Jx5rmS9o\nb0i2RR3FV2xnDO7i5GNw2iuSvsyGVSBe86Ve/uN8vFs4//0V0jTmQwtHGROu/r8O\nbVn6o9jQANFLatLOG7cnVjiRybM1FVgV9FMY11VT0ErDWBEpgPxEvmAUw5M86/Bo\nVf2dvIMOH9XVhLOfQapaVf8=\n-----END PRIVATE KEY-----\n",#os.getenv('PRIVATE_KEY'),
            "client_email": "cww-wash-dashboard-shiny-app@cww-wash-dashboard.iam.gserviceaccount.com",
            "client_id": "103153184028709897384",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/cww-wash-dashboard-shiny-app%40cww-wash-dashboard.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        }
    # Authenticate from dictionary
    return gspread.service_account_from_dict(credentials)

def get_data_file():
    gs_client = initialize_gspread()
    return gs_client.open_by_key(GS_FILE_ID)

DATA_FILE = get_data_file()

advisors = get_as_dataframe(DATA_FILE.worksheet('advisors'))
countries = get_as_dataframe(DATA_FILE.worksheet('countries'))
types = get_as_dataframe(DATA_FILE.worksheet('types')).type.to_list()
risk_matrix = get_as_dataframe(DATA_FILE.worksheet('risk_matrix'))
programmes = get_as_dataframe(DATA_FILE.worksheet('programmes'))
programmes['start_year'] = pd.to_datetime(programmes.start_year, format="%Y", errors='coerce')
programmes['end_year'] = pd.to_datetime(programmes.end_year, format="%Y", errors='coerce')
programmes = programmes.sort_values(by=['end_year', 'start_year'])

def import_calendar():
    calendar = DATA_FILE.worksheet('calendar')
    try:
        data = get_as_dataframe(calendar)
        ## Convert dates to datetime
        data['start_date'] = pd.to_datetime(data.start_date, dayfirst=True, errors='raise', format='mixed')#format='%d-%b-%Y')
        data['end_date'] = pd.to_datetime(data.end_date, dayfirst=True, errors='raise', format='mixed')#format='%d-%b-%Y')
        return data
    except Exception as e:
        print(f'Oops, something went wrong while trying to import the calendar db.\nException: {str(e)}')
        return None

def update_calendar(data):
    calendar = DATA_FILE.worksheet('calendar')
    try:
        calendar.clear()
        set_with_dataframe(calendar, data)
        print(f'Successfully saved to file')
    except Exception as e:
        print(f'Something went wrong: {str(e)}')
    
    ## Format datetime columns in Google Sheets
    # Identify datetime columns
    datetime_columns = data.select_dtypes(include=['datetime64[ns]']).columns    
    datetime_cols_indices = [data.columns.get_loc(col) + 1 for col in datetime_columns]
    for col_index in datetime_cols_indices:
        calendar.format(f'{chr(64 + col_index)}2:{chr(64 + col_index)}{len(data) + 1}', {
            "numberFormat": {
                "type": "DATE_TIME",
                "pattern": "dd-mm-yyyy"
            }
        })
        
def import_country_calls():
    country_calls = DATA_FILE.worksheet('country_calls')
    try:
        data = get_as_dataframe(country_calls)
        ## Convert dates to datetime
        data['date'] = pd.to_datetime(data.date, dayfirst=True, errors='raise', format='mixed')
        return data
    except Exception as e:
        print(f'Oops, something went wrong while trying to import the calls db.\nException: {str(e)}')
        return None

def update_country_calls(data):
    country_calls = DATA_FILE.worksheet('country_calls')
    try:
        country_calls.clear()
        set_with_dataframe(country_calls, data)
        print(f'Successfully saved to file')
    except Exception as e:
        print(f'Something went wrong: {str(e)}')
    
    ## Format datetime columns in Google Sheets
    # Identify datetime columns
    datetime_columns = data.select_dtypes(include=['datetime64[ns]']).columns    
    datetime_cols_indices = [data.columns.get_loc(col) + 1 for col in datetime_columns]
    for col_index in datetime_cols_indices:
        country_calls.format(f'{chr(64 + col_index)}2:{chr(64 + col_index)}{len(data) + 1}', {
            "numberFormat": {
                "type": "DATE_TIME",
                "pattern": "dd-mm-yyyy"
            }
        })

def import_wash_list():
    wash_list = DATA_FILE.worksheet('wash_list')
    try:
        ## import from excel
        data = get_as_dataframe(wash_list)
        return data
    except Exception as e:
        print(f'Oops, something went wrong while trying to import the wash_list db.\nException: {str(e)}')
        return None

## CALENDAR FUNCTIONS ##

def pcg_days_by_type(data, year):
    def total_busdays(data):
        ## calculate the number of business days between two dates
        return len(pd.bdate_range(data.start_date, data.end_date))
    
    data['total_busdays'] = data.apply(total_busdays, axis=1)
    ## Count how many days each advisor spent during the year by type 
    if year != 'All':
        year = int(year)
        data = data[data.end_date.dt.year == year]
        yr_busdays = np.busday_count(str(year), str(year+1))
    else:
        yr_busdays = np.busday_count(str(min(data.start_date.dt.year)), str(max(data.end_date.dt.year)))
    # data_grouped = data[data.end_date.dt.year == int(year)].groupby(['advisor', 'type']).agg({'total_busdays':'sum'}).reset_index()
    data_grouped = data.groupby(['advisor', 'type']).agg({'total_busdays':'sum'}).reset_index()
    
    data_grouped['pcg_busdays'] = (data_grouped.total_busdays / yr_busdays)*100

    return data_grouped

### UI FUNCTIONS ###

def date_prettify(series):
    return series.strftime('%d-%b-%Y')#f'{series:%d-%b-%Y}'

CALENDAR_FORM = {
    'advisor': ui.input_select(
        id='cal_advisor',
        label='',
        ## Create a dictionary with keys = advisor name
        choices={k:k for k in advisors.short_name.sort_values()}
    ),
    'type': ui.input_radio_buttons(
        id='cal_type',
        label='',
        choices=types
    ),
    'start_date': ui.input_date(
        id='cal_start_date',
        label='From:',
        value=datetime.today(),
        format='dd-mm-yyyy',
        min='2024-01-01',
        max=datetime.today() + timedelta(weeks=52)
    ),
    'end_date': ui.input_date(
        id='cal_end_date',
        label='To:',
        value=datetime.today(),
        format='dd-mm-yyyy',
        min='2024-01-01',
        max=datetime.today() + timedelta(weeks=52)
    ),
    'remarks': ui.input_text(
        id='cal_remarks',
        label='Description',
        placeholder='e.g. country name'
    )
}


countries_list = countries['CIA Name'].to_list()
countries_list.append('Hanaano')

CALL_FORM = {
    'date': ui.input_date(
        id='date_call',
        label='Date:',
        value=datetime.today(),
        format='dd-mm-yyyy',
        min='2024-01-01',
        # max=datetime.today() + timedelta(weeks=52)
    ),
    'country': ui.input_select(
        id='country_call',
        label='',
        ## create a dictionary with keys = country names
        # choices={k:k for k in countries['CIA Name'].sort_values()}
        choices={k:k for k in sorted(countries_list)}
    ),
    'sal_attendees': ui.input_select(
        id='sal_attendees_call',
        label='SAL Attendee(s) (use Ctrl for multiselect)',
        choices={k:k for k in sorted(advisors.short_name.unique())},#[k for k in sorted(advisors.short_name.unique())],
        multiple=True
    ),
    # 'sal_attendees': ui.input_text(
    #     id='sal_attendees_call',
    #     label='SAL TA',
    #     placeholder='comma separated names'
    # ),
    'country_attendees': ui.input_text(
        id='country_attendees_call',
        label='Country Attendee(s)',
        placeholder='comma separated names'
    ),
    'category': ui.input_radio_buttons(
        id='category_call',
        label='',
        choices=['scheduled', 'special support', 'training', 'other'],
        selected='scheduled'
    ),
    'description': ui.input_text_area(
        id='description_call',
        label='Description',
        placeholder='e.g., monthly catch-up',
        width='400px',
        height='200px'
    )
}

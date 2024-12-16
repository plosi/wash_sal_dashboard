from shiny import ui
from datetime import datetime, timedelta

from load_data import advisors, countries, wash_list, calendar

def date_prettify(series):
    return f'{series:%d-%b-%Y}'

types = ['Country Support Visit','Bank Holiday','Leave Full Day','Leave Half Day','Time In Lieu Full Day','Time In Lieu Half Day','Conference/Workshop','Training','Personal Commitment (no travel)']

ADD_CAL = {
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
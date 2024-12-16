from shiny import App, render, reactive, ui
from shinywidgets import output_widget, render_widget, render_plotly

from pathlib import Path
from datetime import datetime, timedelta
import faicons as fa
import pandas as pd
import plotly.express as px

import helpers as hp
from load_data import advisors, countries, wash_list, calendar

app_dir = Path(__file__).parent

cal = reactive.Value()
cal.set(calendar)

app_ui = ui.page_navbar(
    # ui.include_css(app_dir / 'css\\styles.css'),
    # ui.panel_title('WASH SAL Dashboard'),
    ui.nav_panel(
        'Calendar',
        ui.layout_columns(
            ui.card(
                ui.card_header(ui.HTML('<h1>Calendar</h1>')),
                ui.row(
                    ui.column(
                        4,
                        ui.input_checkbox_group(
                            id='calendar_advisor_filter',
                            label='Filter by:',
                            choices=[region for region in calendar.advisor.unique()],
                            selected=[region for region in calendar.advisor.unique()],
                            inline=True
                        ),
                    ),
                    ui.column(4),# empty column for nice spacing
                    ui.column(
                        4,
                        ui.input_slider(
                            id='calendar_date_range',
                            label='',
                            min=calendar.start_date.min(),
                            max=calendar.start_date.max() + timedelta(60),
                            value=[datetime.today() - timedelta(30), datetime.today() + timedelta(30)],
                            time_format='%d-%b-%Y'
                        ),
                    ),     
                ),
                output_widget('plot_calendar'),
                full_screen=True
            ),
            ui.card(
                ui.card_header(
                    ui.HTML('<h1>Data</h1>'),
                ),
                ### TO DO: gallery exaample here https://github.com/skaltman/outliers-app-db-python/blob/main/app.py
                ### live app here: https://01922aab-06e0-fc8f-8958-30dd67f9af51.share.connect.posit.cloud/
                ui.row(
                    ui.column(
                        4,
                        ui.markdown('Controls'),
                        ui.input_action_button(
                            id='add_to_calendar',
                            label='Add',
                            icon=fa.icon_svg('calendar-plus')
                        ),
                        ui.input_action_button(
                            id='edit_calendar',
                            label='Edit',
                            icon=fa.icon_svg('pen-to-square'),
                            disabled=True,
                        ),
                        ui.input_action_button(
                            id='delete_from_calendar',
                            label='Delete',
                            icon=fa.icon_svg('calendar-xmark'),
                            disabled=True
                        ),
                        # ui.download_button(id='save_calendar', label='Save'),
                    ),
                    ui.column(
                        8,
                        ui.output_data_frame('calendar_df'),
                    )
                )
            ),
            col_widths=(12)#,6,6)
        )
    ),
    ui.nav_panel(
        'Country Allocation',
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_checkbox_group(
                    id='map_region_filter',
                    label='Filter by:',
                    choices=[region for region in countries.Continent.unique()],
                    selected=[region for region in countries.Continent.unique()]
                )
            ),
            ui.layout_columns(
                ui.card(
                    output_widget('plot_allocation_map'),
                    full_screen=True,
                ),
                ui.card(
                    output_widget('plot_allocation_bar'),
                    full_screen=True
                ),
                col_widths=(8,4)
            ),
        ),
    ),
    ui.nav_panel(
        'Country Calls'
    ),
    ui.nav_panel(
        'Capacity Building'
    ),
    
)


def server(input, output, session):

    @render_widget
    def plot_calendar():
        filtered_calendar = calendar[calendar.advisor.isin(input.calendar_advisor_filter())]

        # Ensure the dataframe is valid
        if filtered_calendar.empty or filtered_calendar[['start_date', 'end_date']].isna().any().any():
            return None  # Return an empty plot or suitable default

        # Handle calendar_date_range
        try:
            range_x_start, range_x_end = input.calendar_date_range()
            ## transform date range into a datetime object to be used in the range_x of px.timeline
            range_x_start = datetime(range_x_start.year, range_x_start.month, range_x_start.day)
            range_x_end = datetime(range_x_end.year, range_x_end.month, range_x_end.day)
            assert range_x_start is not None and range_x_end is not None
        except (TypeError, AssertionError):
            range_x_start, range_x_end = None, None  # Default values if invalid

        hover_data={
            'start_date':False,
            'end_date':False,
            'advisor':False,
            'type':False,
            'from':filtered_calendar.start_date.apply(hp.date_prettify),
            'to':filtered_calendar.end_date.apply(hp.date_prettify)
        }

        fig = px.timeline(
            data_frame=filtered_calendar,
            x_start='start_date',
            x_end='end_date',
            y='advisor',
            color='type',
            hover_name='type',
            hover_data=hover_data,
            text='remarks',
            range_x=[range_x_start, range_x_end] if range_x_start and range_x_end else None,
            labels={'type':'', 'advisor':''}
        )
        fig.update_traces(textposition='inside')
        # fig.update_xaxes(tickformat='%d-%b', dtick=86400000.0*5)

        fig.update_xaxes(
            tickformat='%d-%b', dtick=86400000.0*7,
            rangeslider_visible=False,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label='1M', step='month', stepmode='backward'),
                    dict(count=3, label='3M', step='month', stepmode='backward'),
                    dict(count=6, label='6M', step='month', stepmode='backward'),
                    # dict(count=1, label='YTD', step='year', stepmode='todate'),
                    dict(count=1, label='1Y', step='year', stepmode='backward'),
                    dict(step='all')
                ])
            )
        )

        return fig


    @render_widget
    def plot_allocation_map():
        filtered_countries = countries[countries.Continent.isin(input.map_region_filter())]
        palette = ['#4A628A', '#7AB2D3', '#B9E5E8', '#DFF2EB']

        hover_data = {
            'ta_focal': False,
            'ISO 3166 alpha3': False,
            'Focal TA': filtered_countries.ta_focal,
        }

        fig = px.choropleth(
            data_frame=filtered_countries,
            locations='ISO 3166 alpha3',
            color='ta_focal',
            color_discrete_sequence=palette,
            hover_name='CIA Name',
            hover_data=hover_data,
            labels={'ta_focal': 'Focal Point'},
        )
        fig.update_geos(fitbounds='locations')

        return fig


    @render_widget
    def plot_allocation_bar():
        filtered_countries = countries[countries.Continent.isin(input.map_region_filter())]

        fig = px.bar(
            data_frame=filtered_countries.groupby('ta_focal').agg('count').reset_index(),
            x='ta_focal',
            y='CIA Name',
            labels={'ta_focal':'','CIA Name':'count'}
        )

        return fig


    @render.data_frame
    def calendar_df():
        # tmp = calendar[calendar.advisor.isin(input.calendar_advisor_filter())].copy()
        tmp = calendar.copy()
        tmp['start_date'] = tmp.start_date.apply(hp.date_prettify)
        tmp['end_date'] = tmp.end_date.apply(hp.date_prettify)
        return render.DataGrid(
            tmp,
            width='fit-content',
        )
    

    @reactive.effect
    @reactive.event(input.add_to_calendar)
    def _():
        m = ui.modal(
            hp.ADD_CAL['advisor'],
            hp.ADD_CAL['type'],
            hp.ADD_CAL['start_date'],
            hp.ADD_CAL['end_date'],
            hp.ADD_CAL['remarks'],
            ui.div(
                ui.input_action_button('submit_add_cal', 'Submit', class_='btn btn-primary'),
                class_='d-flex justify-content-end'
            ),
            easy_close=True,
            title='New Calendar Entry',
        )
        ui.modal_show(m)

    @reactive.effect
    @reactive.event(input.submit_add_cal)
    def _():
        try:
            new_row = pd.DataFrame([{k: input[f'add_{k}']() for k in hp.ADD_CAL.keys()}])
            ## make sure that the new dataframe has the same columns order as the original one
            new_row = new_row.reindex(columns=calendar.columns)
            # df['start_date'] = df.start_date.strftime('%d/%m/%Y')
            # df['end_date'] = df.end_date.strftime('%d/%m/%Y')

            updated_cal = pd.concat([calendar, new_row], ignore_index=True)

            cal_file = app_dir / 'data' / 'calendar.csv'

            if not cal_file.exists():
                updated_cal.to_csv(cal_file, mode='w', index=False)#, header=True)
            else:
                updated_cal.to_csv(cal_file, mode='w', index=False)#    , header=False)

            ui.notification_show(f'New entry for {input.add_advisor()} added to the calendar, thank you!', type='message')
            
        except Exception:
            ui.notification_show(f'Oops, something went wrong. Retry!', type='error')


    # @render.download(filename='updated_cal.xlsx')
    # def save_calendar():
    #     yield calendar_df.data_view().to_excel(excel_writer='openpyxl', index=False, sheet_name='calendar')


app = App(app_ui, server)
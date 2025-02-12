from shiny import App, render, reactive, ui
from shinywidgets import output_widget, render_widget

import os
import re
from datetime import datetime, timedelta
import faicons as fa
import pandas as pd
import plotly.express as px
import plotly.io as pio
pio.templates.default = "ggplot2"

import helpers as hp

advisors = hp.advisors
countries = hp.countries
types = hp.types
risk_matrix = hp.risk_matrix
programmes = hp.programmes

calendar = reactive.Value()
wash_list = reactive.Value()
country_calls = reactive.Value()

calendar.set(hp.import_calendar())
wash_list.set(hp.import_wash_list())
country_calls.set(hp.import_country_calls())

app_ui = ui.page_navbar(
    ## TO DO: personal styles
    # ui.include_css(app_dir / 'css' / 'styles.css'),

    ## Calendar Panel
    ui.nav_panel(
        'Calendar',
        ui.layout_columns(
            ui.card(
                ui.card_header(ui.HTML('<h1>Calendar</h1>')),
                ui.row(
                    ui.column(6, ui.output_ui('calendar_advisor_filter')),
                    ui.column(2), ## Empty column for nice spacing
                    ui.column(4, ui.output_ui('calendar_date_range')),     
                ),
                output_widget('plot_calendar'),
                full_screen=True
            ),
            ui.card(
                ui.card_header(ui.HTML('<h1>Data</h1>')),
                ui.row(
                    ui.column(
                        4,
                        ui.markdown('Add | Delete | Edit'),
                        ui.row(
                            ui.column(4, ui.tooltip(ui.output_ui('add_calendar_btn'), 'Add', placement='top')),
                            ui.column(4, ui.tooltip(ui.output_ui('delete_calendar_btn'), 'Delete', placement='top')),
                            ui.column(4, ui.tooltip(ui.output_ui('edit_calendar_btn'), 'Edit', placement='top')),
                        ),
                        ui.HTML('<br>'),
                        ui.row(ui.column(6, ui.output_ui('table_advisor_select'))),
                        ui.row(ui.column(6, ui.output_ui('table_year_select'))),
                        ui.row(ui.column(6, ui.output_ui('table_type_select'))),
                    ),
                    ui.column(8, ui.output_data_frame('calendar_df'))
                )
            ),
            ui.card(
                ui.card_header(ui.HTML('<h1>Stats</h1>')),
                ui.output_ui('select_year'),
                ui.row(
                    ui.column(5, ui.output_data_frame('advisor_occupancy_df')),
                    ui.column(7,
                        output_widget('plot_bar_days_bytype'),
                        full_screen=True
                    ),
                ),
                
            ),
            col_widths=12
        ),
    ),

    ## Country Allocation Panel
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
                ui.card(
                    ui.card_header(ui.HTML('<h1>Data</h1>')),
                    ui.output_data_frame('countries_df')
                    # ui.markdown('Show data table here')
                ),
                col_widths=(8,4,12)
            ),
        ),
    ),

    ## Countries Overview Panel
    ui.nav_panel(
        'Countries Overview',
        ui.card(
            ui.card_header(ui.HTML('<h1>Capacity / Risk</h1>')),
            ui.layout_columns(
                ui.card(
                    output_widget('risk_matrix_map'),
                    full_screen=True,
                ),
                ui.card(
                    ui.output_data_frame('risk_matrix_df'),
                    full_screen=True,
                ),
                col_widths=(8,4)
            ),
        ),
        ui.card(
            ui.card_header(ui.HTML('<h1>Programmes</h1>')),
            ui.row(
                ui.column(
                    4,
                    ui.output_ui('select_year_start_programmes'),
                    ui.output_ui('select_year_end_programmes'),
                    ui.input_switch(id='programmes_donor_switch', label='By Donor')
                ),
                ui.column(8, output_widget('map_programmes'))
            ),
            ui.row(
                output_widget('plot_programmes'),
            )
        )
    ),

    ## Country Calls Panel
    ui.nav_panel(
        'Country Calls',
        ui.layout_columns(
            ui.card(
                ui.card_header(ui.HTML('<h1>Call Registry</h1>')),
                ui.row(
                    ui.column(
                        4,
                        ui.markdown('Add | Delete | Edit'),
                        ui.row(
                            ui.column(4, ui.tooltip(ui.output_ui('add_call_btn'), 'Add', placement='top')),
                            ui.column(4, ui.tooltip(ui.output_ui('delete_call_btn'), 'Delete', placement='top')),
                            ui.column(4, ui.tooltip(ui.output_ui('edit_call_btn'), 'Edit', placement='top')),
                        ),
                        ui.HTML('<br>'),
                        ui.row(ui.column(6, ui.output_ui('call_country_select')),),
                        ui.row(ui.column(6, ui.output_ui('call_year_select')),),
                    ),
                    ui.column(8, ui.output_data_frame('calls_df'),)
                )
            ),
            ui.card(
                ui.card_header(ui.HTML('<h1>Stats</h1>')),
                ui.row(
                    ui.column(
                        4,
                        ui.output_ui('call_year_select_2'),
                    ),
                ),
                ui.row(
                    ui.column(
                        6,
                        output_widget('plot_bar_calls_bycountry'),
                    ),
                    ui.column(
                        6,
                        output_widget('plot_bar_calls_byadvisor'),
                    ),
                    full_screen=True
                    # ui.column(
                    #     4,
                    #     ui.input_slider(
                    #         id='min_calls_slider',
                    #         label='Minimum number of calls',
                    #         min=1,
                    #         max=10,
                    #         pre='>=',
                    #         ticks=True,
                    #         step=3,
                    #         value=1
                    #     ),
                    # )
                ),
                
            ),
            col_widths=12
        )
    ),

    ## Proposals Panel
    ui.nav_panel(
        'Proposals',
        ui.markdown('Under construction'),
    ),

    ## Files Panel
    ui.nav_panel(
        'Files',
        ui.markdown('Link to the database.'),
        ui.markdown('You can view, print and download the file in excel format.'),
        ui.HTML(f'<a href="{hp.url}" target="_blank">Click here</a>')
    ),
    title='WASH SAL Dashboard',
)


def server(input, output, session):
    ##
    ## Calendar - Calendar
    ##
    @render.ui
    def calendar_advisor_filter():
        data = calendar.get()
        return ui.input_checkbox_group(
                    id='calendar_advisor_filter_',
                    label='Filter by:',
                    choices=[advisor for advisor in data.advisor.unique()],
                    selected=[advisor for advisor in data.advisor.unique()],
                    inline=True
                )

    @render.ui
    def calendar_date_range():
        data = calendar.get()
        return ui.input_slider(
                    id='calendar_date_range_',
                    label='',
                    min=data.start_date.min(),
                    max=datetime.today() + timedelta(weeks=52),
                    value=[datetime.today() - timedelta(weeks=2), datetime.today() + timedelta(weeks=6)],
                    step=14,
                    ticks=True,
                    time_format='%d-%b-%Y'
                ),

    @render_widget
    def plot_calendar():
        data = calendar.get()
        filtered_calendar = data[data.advisor.isin(input.calendar_advisor_filter_())]
        ## If remarks is nan it creates an error when plotting (cannot create JSON object from nan)
        ## TO DO this is a temporary workaround, find another way to fix this!
        filtered_calendar['remarks'] = filtered_calendar.remarks.fillna(' ')

        ## Ensure the dataframe is valid
        if filtered_calendar.empty or filtered_calendar[['start_date', 'end_date']].isna().any().any():
            return None  # Return an empty plot or suitable default

        ## Handle calendar_date_range
        try:
            range_x_start, range_x_end = input.calendar_date_range_()
            ## Transform date range into a datetime object to be used in the range_x of px.timeline
            range_x_start = datetime(range_x_start.year, range_x_start.month, range_x_start.day)
            range_x_end = datetime(range_x_end.year, range_x_end.month, range_x_end.day)
            assert range_x_start is not None and range_x_end is not None
        except (TypeError, AssertionError):
            range_x_start, range_x_end = None, None  # Default values if invalid

        ## eEnsure that single days events are represented with a visible width
        single_day_mask = filtered_calendar.start_date == filtered_calendar.end_date
        filtered_calendar.loc[single_day_mask, 'end_date'] = filtered_calendar.end_date + timedelta(hours=11, minutes=59)

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
            color_discrete_map=dict(zip(types, hp.TYPE_PALETTE)),
            hover_name='type',
            hover_data=hover_data,
            text='remarks',
            range_x=[range_x_start, range_x_end] if range_x_start and range_x_end else None,
            labels={'type':'', 'advisor':''}
        )
        fig.update_xaxes(
            tickformat='%d-%b', dtick=86400000.0*7,
            rangeslider_visible=False,
            # rangeselector=dict(
            #     buttons=list([
            #         dict(count=1, label='1M', step='month', stepmode='backward'),
            #         dict(count=3, label='3M', step='month', stepmode='backward'),
            #         dict(count=6, label='6M', step='month', stepmode='backward'),
            #         # dict(count=1, label='YTD', step='year', stepmode='todate'),
            #         dict(count=1, label='1Y', step='year', stepmode='backward'),
            #         dict(step='all')
            #     ])
            # )
        )
        fig.update_traces(textposition='inside')
        fig.add_vline(x=datetime.today(), line_dash='dot', line_width=3, opacity=1, line_color='black')

        return fig

    ##
    ## Calendar - Data
    ##
    @render.data_frame
    def calendar_df():
        df = calendar.get()
        data = df.copy()

        ## Apply filters while preserving original indices
        if input.table_year_select_() != 'All':
            data = data[data.end_date.dt.year == int(input.table_year_select_())]
        if input.table_advisor_select_() != 'All':
            data = data[data.advisor==input.table_advisor_select_()]
        if input.table_type_select_() != 'All':
            data = data[data.type==input.table_type_select_()]

        data['start_date'] = data.start_date.dt.strftime('%d-%m-%Y')#apply(hp.date_prettify)
        data['end_date'] = data.end_date.dt.strftime('%d-%m-%Y')#.apply(hp.date_prettify)

        return render.DataGrid(
            data.sort_index(ascending=False),
            width='fit-content',
            selection_mode='rows',
            height="300px"
        )

    @render.ui
    def add_calendar_btn():
        return ui.input_action_button(
            id='add_to_calendar',
            label='',
            class_='btn btn-success',
            icon=fa.icon_svg('calendar-plus')
        )

    @render.ui
    def delete_calendar_btn():
        return ui.input_action_button(
                    id='delete_from_calendar_',
                    label='',
                    icon=fa.icon_svg('calendar-xmark'),
                    class_='btn btn-outline-danger',
                )

    @render.ui
    def edit_calendar_btn():
        return ui.input_action_button(
            id='edit_row_',
            label='',
            class_='btn btn-outline-warning',
            icon=fa.icon_svg('pen-to-square'),
        )

    @render.ui
    def table_advisor_select():
        data = calendar.get()
        advisors = [advisor for advisor in data.advisor.unique()]
        advisors.append('All')
        return ui.input_select(
            id='table_advisor_select_',
            label='Filter by advisor:',
            choices = advisors,
            selected='All',
            width='150px'
        )

    @render.ui
    def table_year_select():
        data = calendar.get()
        years = [yr for yr in data.end_date.dt.year]
        years.append('All')
        return ui.input_select(
                    id='table_year_select_',
                    label='Filter by year (end):',
                    choices=years,
                    selected='All',
                    width='150px'
                )
    
    @render.ui
    def table_type_select():
        data = calendar.get()
        types = [type for type in data.type.unique()]
        types.append('All')
        return ui.input_select(
                    id='table_type_select_',
                    label='Filter by type:',
                    choices=types,
                    selected='All',
                    width='150px'
                )

    @reactive.effect
    @reactive.event(input.add_to_calendar)
    def _():
        m = ui.modal(
            hp.CALENDAR_FORM['advisor'],
            hp.CALENDAR_FORM['type'],
            hp.CALENDAR_FORM['start_date'],
            hp.CALENDAR_FORM['end_date'],
            hp.CALENDAR_FORM['remarks'],
            ui.div(
                ui.input_action_button('submit_add_cal', 'Submit', class_='btn btn-primary'),
                class_='d-flex justify-content-end'
            ),
            easy_close=True,
            footer=None,
            title='New Calendar Entry',
        )
        # try:
        #     ui.update_date('cal_end_date', min=input.cal_start_date())
        # except LookupError as e:
        #     print(f'{e}')
        ui.modal_show(m)

    @reactive.effect
    @reactive.event(input.submit_add_cal)
    def _():
        data = calendar.get()
        try:
            new_row = pd.DataFrame([{k: input[f'cal_{k}']() for k in hp.CALENDAR_FORM.keys()}])
            ## Make sure that the new dataframe has the same columns as the original one and that the dates are datetime objects
            new_row = new_row.reindex(columns=data.columns)
            new_row['start_date'] = pd.to_datetime(new_row.start_date, dayfirst=True, errors='raise', format='mixed')
            new_row['end_date'] = pd.to_datetime(new_row.end_date, dayfirst=True, errors='raise', format='mixed')
            ## Add the new row to the existing dataframe and update the reactive value
            updated_cal = pd.concat([data, new_row], ignore_index=True)
            calendar.set(updated_cal)
            ## Save the calendar to file
            hp.update_calendar(updated_cal)
            ui.notification_show(f'New entry for {input.cal_advisor()} added to the calendar, file saved, thank you!', type='message')
        except Exception as e:
            ui.notification_show(f'Oops, something went wrong: {str(e)}. Retry!', type='error')

    @reactive.effect
    @reactive.event(input.delete_from_calendar_)
    def _():
        # Get the index of the selected row(s)
        selected_rows = calendar_df.cell_selection()['rows']
        if not selected_rows:
            ui.notification_show('Please select one or more rows to be deleted', type='error')
            return
        # Get the filtered dataframe view
        filtered_df = calendar_df.data_view()
        ## Map the selected row indices from the filtered view to the original dataframe indices
        selected_original_indices = filtered_df.iloc[[int(r) for r in selected_rows]].index.tolist()
        # Get the original dataframe and remove the selected rows using their original indices
        updated_data = calendar.get().drop(selected_original_indices)
        calendar.set(updated_data)
        hp.update_calendar(updated_data)
        ui.notification_show(f'Removing the following row(s): {[id for id in selected_original_indices]}', type='message')

    @reactive.effect
    @reactive.event(input.edit_row_)
    def _():
        ## Get the indices of the selected rows in the current view (filtered or unfiltered)
        selected_rows = calendar_df.cell_selection()['rows'] ## this is a tuple
        ## Check if you have at least one and only one row selected
        if len(selected_rows) != 1:
            ui.notification_show('Please select at least one and only one row for editing', type='error')
            return
        
        m = ui.modal(
            hp.CALENDAR_FORM['advisor'],
            hp.CALENDAR_FORM['type'],
            hp.CALENDAR_FORM['start_date'],
            hp.CALENDAR_FORM['end_date'],
            hp.CALENDAR_FORM['remarks'],
            ui.div(
                ui.input_action_button('submit_edit_cal', 'Submit', class_='btn btn-primary'),
                class_='d-flex justify-content-end'
            ),
            easy_close=True,
            footer=None,
            title='Edit Calendar Row',
        )

        ## Get the filtered dataframe view and map to original index
        filtered_df = calendar_df.data_view()
        original_index = filtered_df.iloc[int(selected_rows[0])].name

        ## Get the original row data using the mapped index
        original_df = calendar.get()
        row_to_edit = original_df.loc[[original_index]]

        ui.update_select('cal_advisor', selected=row_to_edit.advisor.iloc[0])
        ui.update_radio_buttons('cal_type', selected=row_to_edit.type.iloc[0])
        ui.update_date('cal_start_date', value=row_to_edit.start_date.iloc[0])
        ui.update_date('cal_end_date', value=row_to_edit.end_date.iloc[0])
        ui.update_text('cal_remarks', value='' if pd.isna(row_to_edit.remarks.iloc[0]) else row_to_edit.remarks.iloc[0])

        ui.modal_show(m)

    @reactive.effect
    @reactive.event(input.submit_edit_cal)
    def _():
        ui.modal_remove()
        selected_rows = calendar_df.cell_selection()['rows']
        filtered_df = calendar_df.data_view()
        original_index = filtered_df.iloc[int(selected_rows[0])].name

        ## Update specific row using the original index
        updated_row = pd.DataFrame([{k: input[f'cal_{k}']() for k in hp.CALENDAR_FORM.keys()}])
        original_df = calendar.get()
        updated_row = updated_row.reindex(columns=original_df.columns)
        updated_row.index = [original_index]

        try:
            original_df.update(updated_row)
            calendar.set(original_df)
            hp.update_calendar(original_df)
            ui.notification_show(f'Updated entry for {updated_row.advisor.iloc[0]}, thank you!', type='message')   
        except Exception:
            ui.notification_show(f'Oops, something went wrong. Retry!', type='error')

    ##
    ## Calendar - Stats
    ##
    @render.ui
    def select_year():
        data = calendar.get()
        years = [yr for yr in data.end_date.dt.year]
        years.append('All')
        return ui.input_select(
                    id='select_year_',
                    label='Filter by year:',
                    choices=years,
                    selected=datetime.today().year,
                    width='150px'
                )

    @render.data_frame
    def advisor_occupancy_df():
        year = input.select_year_()
        df = calendar.get()
        data = hp.pcg_days_by_type(df.copy(), year)
        data['pcg_busdays'] = (data.pcg_busdays/100).map('{:.2%}'.format)
        data.columns = ['Advisor', 'Type', '# Days', '%']

        return render.DataTable(
            data.sort_index(ascending=False),
            width='fit-content',
            selection_mode='rows'
        )

    @render_widget
    def plot_bar_days_bytype():
        year = input.select_year_()
        tmp = calendar.get()
        ## calculate the percentages on a copy of the dataframe so that the original is not changed
        # data = hp.pcg_days_by_type(tmp.copy(), int(year))
        data = hp.pcg_days_by_type(tmp.copy(), year)

        fig = px.bar(
            data_frame = data,
            x='total_busdays',
            y='type',
            color='advisor',
            color_discrete_map=dict(zip(sorted(advisors.short_name), hp.ADVISOR_PALETTE)),
            barmode='group',
            labels={'type': '', 'advisor':'', 'total_busdays': 'Total business days'}
        )
        fig.update_layout(legend=dict(y=1.1, orientation='h'))

        return fig

    ###
    ### Country Allocation ###
    ###
    @render_widget
    def plot_allocation_map():
        filtered_countries = countries[countries.Continent.isin(input.map_region_filter())]

        hover_data = {
            'ta_focal': False,
            'ISO 3166 alpha3': False,
            'Focal TA': filtered_countries.ta_focal,
        }

        fig = px.choropleth(
            data_frame=filtered_countries,
            locations='ISO 3166 alpha3',
            color='ta_focal',
            # color_discrete_sequence=hp.ADVISOR_PALETTE,
            color_discrete_map=dict(zip(sorted(advisors.short_name), hp.ADVISOR_PALETTE)),
            hover_name='CIA Name',
            hover_data=hover_data,
            labels={'ta_focal': 'Focal Point'},
        )
        fig.update_geos(fitbounds='locations')
        fig.update_layout(legend=dict(y=1.1, orientation='h'))

        return fig
    
    @render.data_frame
    def countries_df():
        data = countries.copy()
        data.columns = ['Country', 'ISO', 'Continent', 'TA Focal', 'TA Support']
        # data = data.groupby(['TA Focal'])
        filtered_data = data[data.Continent.isin(input.map_region_filter())].drop(['ISO'], axis=1)

        return render.DataTable(
            filtered_data.sort_values(['TA Focal', 'Continent']),
            width='fit-content',
            height="300px"
        )


    @render_widget
    def plot_allocation_bar():
        filtered_countries = countries[countries.Continent.isin(input.map_region_filter())]

        fig = px.bar(
            data_frame=filtered_countries.groupby('ta_focal').agg('count').reset_index(),
            x='ta_focal',
            y='CIA Name',
            color='ta_focal',
            # color_discrete_sequence=hp.ADVISOR_PALETTE,
            color_discrete_map=dict(zip(sorted(advisors.short_name), hp.ADVISOR_PALETTE)),
            labels={'ta_focal':'','CIA Name':'Number of countries'}
        )

        fig.update_layout(xaxis={'categoryorder':'total descending'}, showlegend=False)

        return fig

    ###
    ### Countries Overview ###
    ###
    @render_widget
    def risk_matrix_map():
        matrix_df = risk_matrix
        countries_df = countries
        matrix_df['remarks'] = matrix_df.remarks.fillna('-')

        merged = pd.merge(
            left=matrix_df,
            right=countries_df[['CIA Name','ISO 3166 alpha3']],
            left_on='country',
            right_on='CIA Name',
            right_index=False,
        )

        hover_data = {
            'country': False,
            'ISO 3166 alpha3': False,
            'score': False,
            'Description': merged.description,
            'Remarks': merged.remarks,
        }

        fig = px.choropleth(
            data_frame=merged,
            locations='ISO 3166 alpha3',
            color='score',
            color_continuous_scale='RdYlGn_r',
            hover_name='country',
            hover_data=hover_data,
            labels={'country': 'Country', 'description': 'Description', 'remarks': 'Remarks'},
            title="Country classification by WASH/Engineering capacity/risk"
        )
        fig.update_geos(fitbounds='locations')
        fig.update_layout(legend=dict(y=1.1, orientation='h'))

        return fig

    @render.data_frame
    def risk_matrix_df():
        data = risk_matrix.copy()
        data.columns = ['Country', 'Score', 'Description', 'Remarks']
        data = data.sort_values(['Score', 'Country'])
        data = data.drop(['Score'], axis=1)

        return render.DataTable(
            data,
            width='fit-content',
            height="300px"
        )

    @render.ui
    def select_year_start_programmes():
        data = programmes.copy()
        # data = data.sort_values(data.end_year)
        # years = [yr for yr in data.end_year.unique()]
        
        return ui.input_select(
                    id='select_year_start_programmes_',
                    label='Filter by year (starting):',
                    choices=[yr for yr in data.start_year.dt.year],
                    selected=datetime.today().year,
                    width='200px'
                )

    @render.ui
    def select_year_end_programmes():
        data = programmes.copy()
        # data = data.sort_values(data.end_year)
        # years = [yr for yr in data.end_year.unique()]
        
        return ui.input_select(
                    id='select_year_end_programmes_',
                    label='Filter by year (ending):',
                    choices=[yr for yr in data.end_year.dt.year],
                    selected=datetime.today().year,
                    width='200px'
                )

    @render_widget
    def map_programmes():
        min_year = input.select_year_start_programmes_()
        max_year = input.select_year_end_programmes_()
        df = programmes.copy()
        period = f"{min_year} - {max_year}"

        df = df[(df.start_year.dt.year >= int(min_year)) & (df.end_year.dt.year <= int(max_year))]
        df = df.groupby(['country','sub_sector']).agg({'code':'count'}).reset_index().rename(columns={'code':'no_programmes'})
        

        merged = pd.merge(
            left=df,
            right=countries[['CIA Name','ISO 3166 alpha3']],
            left_on='country',
            right_on='CIA Name',
            right_index=False,
        )

        fig = px.scatter_geo(
            data_frame=merged,
            locations="ISO 3166 alpha3",
            # color="continent",
            hover_name="country",
            size="no_programmes",
            projection="natural earth",
            opacity=1,
            title=f"WASH/Engineering Programmes ({period})"
        )

        return fig

    @render_widget
    def plot_programmes():
        min_year = input.select_year_start_programmes_()
        max_year = input.select_year_end_programmes_()
        
        donor_switch = input.programmes_donor_switch()
        df = programmes.copy()

        ## Group by country and filter by date
        df = df[(df.start_year.dt.year >= int(min_year)) & (df.end_year.dt.year <= int(max_year))]
        period = f"{min_year} - {max_year}"
        if not donor_switch:
            data = df.groupby(['country','sub_sector']).agg({'code':'count'}).reset_index().rename(columns={'code':'no_programmes'})
            labels = {'country': '', 'no_programmes': 'Total number of programmes', 'sub_sector': 'Sector'}
            color = 'sub_sector'
        else:
            data = df.groupby(['country','donor']).agg({'code':'count'}).reset_index().rename(columns={'code':'no_programmes'})
            labels = {'country': '', 'no_programmes': 'Total number of programmes', 'donor': 'Donor'}
            color = 'donor'

        fig = px.bar(
            data_frame = data,
            x='country',
            y='no_programmes',
            color=color,
            color_discrete_sequence=px.colors.sequential.Plasma_r,
            labels=labels,
            title=f"Total number of programmes with WASH/Engineering component by country ({period})"
        )

        fig.update_layout(xaxis={'categoryorder':'total descending'})
        fig.update_xaxes(tickangle=45)

        return fig


    ###
    ### Country Calls ###
    ###
    @render.data_frame
    def calls_df():
        df = country_calls.get()
        data = df.copy()
        data['date'] = pd.to_datetime(data.date, dayfirst=True)

        ## Apply filters while preserving original indices
        if input.call_year_select_() != 'All':
            data = data[data.date.dt.year == int(input.call_year_select_())]
        if input.call_country_select_() != 'All':
            data = data[data.country==input.call_country_select_()]
        
        data = data.sort_values(by='date', ascending=False)
        data['date'] = data.date.dt.strftime('%d-%m-%Y')

        return render.DataGrid(
            data,
            width='fit-content',
            selection_mode='rows',
            height="300px"
        )

    @render.ui
    def add_call_btn():
        return ui.input_action_button(
            id='add_call',
            label='',
            class_='btn btn-success',
            icon=fa.icon_svg('calendar-plus')
        )

    @render.ui
    def delete_call_btn():
        return ui.input_action_button(
                id='delete_call_',
                label='',
                icon=fa.icon_svg('calendar-xmark'),
                class_='btn btn-outline-danger',
            )

    @render.ui
    def edit_call_btn():
        return ui.input_action_button(
                id='edit_call_row_',
                label='',
                class_='btn btn-outline-warning',
                icon=fa.icon_svg('pen-to-square'),
            )
                
    @render.ui
    def call_country_select():
        data = country_calls.get()
        countries = [c for c in data.country.unique()]
        countries.append('All')
        return ui.input_select(
            id='call_country_select_',
            label='Filter by country:',
            choices = countries,
            selected='All',
            width='150px'
        )
    
    @render.ui
    def call_year_select():
        data = country_calls.get()
        years = [int(yr) for yr in data.date.dt.year.unique()]
        years.append('All')
        return ui.input_select(
            id='call_year_select_',
            label='Filter by year:',
            choices = years,
            selected='All',
            width='150px'
        )

    @reactive.effect
    @reactive.event(input.add_call)
    def _():
        m = ui.modal(
            hp.CALL_FORM['date'],
            hp.CALL_FORM['country'],
            hp.CALL_FORM['sal_attendees'],
            hp.CALL_FORM['country_attendees'],
            hp.CALL_FORM['category'],
            hp.CALL_FORM['description'],
            ui.div(
                ui.input_action_button('submit_add_country_call', 'Submit', class_='btn btn-primary'),
                class_='d-flex justify-content-end'
            ),
            easy_close=True,
            footer=None,
            title='Add Country Call',
        )
        ui.modal_show(m)

    @reactive.effect
    @reactive.event(input.submit_add_country_call)
    def _():
        data = country_calls.get()
        try:
            new_row = pd.DataFrame([{k: input[f'{k}_call']() for k in hp.CALL_FORM.keys()}])
            ## Make sure that the new dataframe has the same columns as the original one and that the dates are datetime objects
            new_row = new_row.reindex(columns=data.columns)
            new_row['date'] = pd.to_datetime(new_row.date, dayfirst=True, errors='raise', format='mixed')
            ## Split multiple names in sal_attendees into comma separated string
            new_row['sal_attendees'] = re.sub("[()']", "", ", ".join(map(str, new_row.sal_attendees))).strip(",")

            ## Add the new row to the existing dataframe and update the reactive value
            updated_df = pd.concat([data, new_row], ignore_index=True)
            country_calls.set(updated_df)
            ## Save the call registry to file
            hp.update_country_calls(updated_df)
            # ui.notification_show(f'New entry for country call added to the country calls registry, thank you!', type='message')
            ui.notification_show(f'New entry for {input.country_call()} added to the country calls registry, thank you!', type='message')   
        except Exception as e:
            ui.notification_show(f'Oops, something went wrong: {str(e)}. Retry!', type='error')

    @reactive.effect
    @reactive.event(input.delete_call_)
    def _():
        # Get the index of the selected row(s)
        selected_rows = calls_df.cell_selection()['rows']
        if not selected_rows:
            ui.notification_show('Please select one or more rows to be deleted', type='error')
            return
        # Get the filtered dataframe view
        filtered_df = calls_df.data_view()
        ## Map the selected row indices from the filtered view to the original dataframe indices
        selected_original_indices = filtered_df.iloc[[int(r) for r in selected_rows]].index.tolist()
        # Get the original dataframe and remove the selected rows using their original indices
        updated_data = country_calls.get().drop(selected_original_indices)
        country_calls.set(updated_data)
        hp.update_country_calls(updated_data)
        ui.notification_show(f'Removing the following row(s): {[id for id in selected_original_indices]}', type='message')

    @reactive.effect
    @reactive.event(input.edit_call_row_)
    def _():
        ## Get the indices of the selected rows in the current view (filtered or unfiltered)
        selected_rows = calls_df.cell_selection()['rows'] ## this is a tuple

        ## check if you have at least one and only one row selected
        if len(selected_rows) != 1:
            ui.notification_show('Please select at least one and only one row for editing', type='error')
            return
        
        m = ui.modal(
            hp.CALL_FORM['date'],
            hp.CALL_FORM['country'],
            hp.CALL_FORM['sal_attendees'],
            hp.CALL_FORM['country_attendees'],
            hp.CALL_FORM['category'],
            hp.CALL_FORM['description'],
            ui.div(
                ui.input_action_button('submit_edit_country_call', 'Submit', class_='btn btn-primary'),
                class_='d-flex justify-content-end'
            ),
            easy_close=True,
            footer=None,
            title='Edit Country Call',
        )
        
        ## Get the filtered dataframe view and map to original index
        filtered_df = calls_df.data_view()
        original_index = filtered_df.iloc[int(selected_rows[0])].name

        ## Get the original row data using the mapped index
        original_df = country_calls.get()
        row_to_edit = original_df.loc[[original_index]]

        ui.update_date('date_call', value=row_to_edit.date.iloc[0])
        ui.update_select('country_call', selected=row_to_edit.country.iloc[0])
        ui.update_text('sal_attendees_call', value=row_to_edit.sal_attendees.iloc[0])
        ui.update_text('country_attendees_call', value=row_to_edit.country_attendees.iloc[0])
        ui.update_radio_buttons('category_call', selected=row_to_edit.category.iloc[0])
        ui.update_text_area('description_call', value='' if pd.isna(row_to_edit.description.iloc[0]) else row_to_edit.description.iloc[0])

        ui.modal_show(m)

    @reactive.effect
    @reactive.event(input.submit_edit_country_call)
    def _():
        ui.modal_remove()
        selected_rows = calls_df.cell_selection()['rows']
        filtered_df = calls_df.data_view()
        original_index = filtered_df.iloc[int(selected_rows[0])].name

        ## Update specific row using the original index
        updated_row = pd.DataFrame([{k: input[f'{k}_call']() for k in hp.CALL_FORM.keys()}])
        original_df = country_calls.get()
        updated_row = updated_row.reindex(columns=original_df.columns)
        updated_row.index = [original_index]

        try:
            original_df.update(updated_row)
            country_calls.set(original_df)
            hp.update_country_calls(original_df)
            ui.notification_show(f'Updated entry for {updated_row.country.iloc[0]}, thank you!', type='message')   
        except Exception:
            ui.notification_show(f'Oops, something went wrong. Retry!', type='error')        

    @render.ui
    def call_year_select_2():
        data = country_calls.get()
        years = [int(yr) for yr in data.date.dt.year.unique()]
        selected_year = max(years)
        years.append('All')
        return ui.input_select(
            id='call_year_select_2_',
            label='Filter by year:',
            choices = years,
            selected=selected_year,
            width='150px'
        )

    @render_widget
    def plot_bar_calls_bycountry():
        year = input.call_year_select_2_()
        # min_calls = int(input.min_calls_slider())
        tmp = country_calls.get()
        ## group by country and filter by date
        if year == 'All':
            df = tmp
            period = f"{tmp.date.dt.year.min()} - {tmp.date.dt.year.max()}"
        else:
            df = tmp[tmp.date.dt.year == int(year)]
            period = year
        data = df.groupby(['country']).agg({'sal_attendees':'count'}).reset_index().rename(columns={'sal_attendees':'no_calls'})

        fig = px.bar(
            # data_frame = data[data.no_calls >= min_calls],
            data_frame = data,
            x='country',
            y='no_calls',
            # x='no_calls',
            # y='country',
            color='no_calls',
            color_continuous_scale='Blues',
            labels={'country': '', 'no_calls': 'Total number of calls'},
            title=f"Total number of calls by country ({period})"
        )

        # fig.update_layout(yaxis={'categoryorder':'total ascending'})
        fig.update_layout(xaxis={'categoryorder':'total descending'})
        fig.update_xaxes(tickangle=45)
        fig.update_coloraxes(showscale=False)

        return fig

    @render_widget
    def plot_bar_calls_byadvisor():
        year = input.call_year_select_2_()
        tmp = country_calls.get()
        tmp = tmp.copy()

        ## Transform the sal_attendees column into a column of lists 
        def sal_attendees_to_list(series):
            return series.split(', ')
        
        tmp['sal_attendees'] = tmp.sal_attendees.apply(sal_attendees_to_list)
        
        ## group by advisor and filter by date
        if year == 'All':
            df = tmp
            period = f"{tmp.date.dt.year.min()} - {tmp.date.dt.year.max()}"
        else:
            df = tmp[tmp.date.dt.year == int(year)]
            period = year

        df = df.explode('sal_attendees')
        data = df.groupby(['sal_attendees']).agg({'country':'count'}).reset_index().rename(columns={'country':'no_calls'})

        fig = px.bar(
            # data_frame = data[data.no_calls >= min_calls],
            data_frame = data,
            x='sal_attendees',
            y='no_calls',
            # x='no_calls',
            # y='sal_attendees',
            color='no_calls',
            color_continuous_scale='Reds',
            labels={'sal_attendees': '', 'no_calls': 'Total number of calls'},
            title=f"Total number of calls by advisor ({period})"
        )

        # fig.update_layout(yaxis={'categoryorder':'total ascending'})
        fig.update_layout(xaxis={'categoryorder':'total descending'})
        fig.update_xaxes(tickangle=45)

        return fig

    @render.download(filename='wash_sal_db.xlsx')
    def download_db_xlsx():
        from io import BytesIO
        
        # Get the spreadsheet
        file = hp.get_data_file()
        
        # Create Excel writer object with BytesIO buffer
        buffer = BytesIO()
        writer = pd.ExcelWriter(buffer, engine='openpyxl')
        
        # Get all worksheets
        for worksheet in file.worksheets():
            # Get values from each worksheet
            values = worksheet.get_all_values()
            
            # Convert to DataFrame
            if values:  # Check if worksheet is not empty
                df = pd.DataFrame(values[1:], columns=values[0])
                
                # Write each worksheet to the Excel file
                df.to_excel(writer, 
                          sheet_name=worksheet.title,
                          index=False)
        
        # Save and get the content
        writer.close()
        buffer.seek(0)
        return buffer.getvalue()
    
    # @render.download()
    # def download_db_xlsx():
    #     path = os.path.join(os.path.dirname(__file__), 'data', 'database.xlsx')
    #     return path

app = App(app_ui, server)

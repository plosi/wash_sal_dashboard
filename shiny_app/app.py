from shiny import App, render, reactive, ui
from shinywidgets import output_widget, render_widget, render_plotly

import os
from datetime import datetime, timedelta
import faicons as fa
import pandas as pd
import plotly.express as px

import helpers as hp

advisors = hp.advisors
countries = hp.countries
types = hp.types

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
                    ui.column(
                        4,
                        ui.output_ui('calendar_advisor_filter')
                    ),
                    ui.column(1),## empty column for nice spacing
                    ui.column(
                        4,
                        ui.output_ui('calendar_date_range')
                    ),     
                ),
                output_widget('plot_calendar'),
                full_screen=True
            ),
            ui.card(
                ui.card_header(ui.HTML('<h1>Data</h1>')),
                ### TO DO: gallery example here https://github.com/skaltman/outliers-app-db-python/blob/main/app.py
                ### live app here: https://01922aab-06e0-fc8f-8958-30dd67f9af51.share.connect.posit.cloud/
                ui.row(
                    ui.column(
                        4,
                        ui.markdown('Add / Delete / Edit'),
                        ui.row(
                            ui.column(
                                4,
                                ui.tooltip(
                                    ui.input_action_button(
                                        id='add_to_calendar',
                                        label='',
                                        icon=fa.icon_svg('calendar-plus'),
                                        class_='btn btn-outline-success'
                                    ),
                                    'Add',
                                    placement='top'                                    
                                )
                            ),
                            ui.column(
                                4,
                                ui.tooltip(
                                    ui.output_ui('delete_from_calendar'),
                                    'Delete',
                                    placement='top'
                                ),
                            ),
                            ui.column(
                                4,
                                ui.tooltip(
                                    ui.output_ui('edit_row'),
                                    'Edit',
                                    placement='top'
                                )
                            ),
                        ),
                        ui.HTML('<br>'),
                        ui.row(
                            ui.column(
                                6,
                                ui.output_ui('table_advisor_select')
                            ),
                        ),
                        ui.row(
                            ui.column(
                                6,
                                ui.output_ui('table_year_select')
                            ),
                        ),
                        ui.row(
                            ui.column(
                                6,
                                ui.output_ui('table_type_select')
                            ),
                        ),
                    ),
                    ui.column(
                        8,
                        ui.output_data_frame('calendar_df'),
                    )
                )
            ),
            ui.card(
                ui.card_header(ui.HTML('<h1>Stats</h1>')),
                ui.output_ui('select_year'),
                output_widget('plot_bar_days_bytype'),
                full_screen=True
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
                    ui.markdown('Show data table here')
                ),
                col_widths=(8,4,12)
            ),
        ),
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
                        ui.markdown('Add / Delete / Edit'),
                        ui.row(
                            ui.column(
                                4,
                                ui.tooltip(
                                    ui.input_action_button(
                                        id='add_call',
                                        label='',
                                        icon=fa.icon_svg('calendar-plus'),
                                        class_='btn btn-outline-success'
                                    ),
                                    'Add',
                                    placement='top'
                                ),
                            ),
                            ui.column(
                                4,
                                ui.tooltip(
                                    ui.output_ui('delete_call'),
                                    'Delete',
                                    placement='top'
                                )
                            ),
                            ui.column(
                                4,
                                ui.tooltip(
                                    ui.output_ui('edit_call_row'),
                                    'Edit',
                                    placement='top'
                                )
                            ),
                        ),
                        ui.HTML('<br>'),
                        ui.row(
                            ui.column(
                                6,
                                ui.output_ui('call_country_select')
                            ),
                        ),
                        ui.row(
                            ui.column(
                                6,
                                ui.output_ui('call_year_select')
                            ),
                        ),
                    ),
                    ui.column(
                        8,
                        ui.output_data_frame('calls_df'),
                    )
                )
            ),
            ui.card(
                ui.card_header(ui.HTML('<h1>Stats</h1>')),
                ui.row(
                    ui.column(
                        4,
                        ui.output_ui('call_year_select_2'),
                    ),
                    ui.column(4),
                    ui.column(
                        4,
                        ui.input_slider(
                            id='min_calls_slider',
                            label='Minimum number of calls',
                            min=1,
                            max=10,
                            pre='>=',
                            ticks=True,
                            step=3,
                            value=4
                        ),
                    )
                ),
                output_widget('plot_bar_calls_bycountry'),
                full_screen=True
            ),
            col_widths=12
        )
    ),

    ## Files Panel
    ui.nav_panel(
        'Files',
        ui.markdown('Download the database in excel format'),
        ui.download_button(
            id='download_db_xlsx',
            label='Download',
        )
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
                    min=data.start_date.min(),#pd.to_datetime(data.start_date).min(),
                    max=data.start_date.max() + timedelta(60),#pd.to_datetime(data.start_date).max() + timedelta(60),
                    value=[datetime.today() - timedelta(30), datetime.today() + timedelta(30)],
                    time_format='%d-%b-%Y'
                ),

    @render_widget
    def plot_calendar():
        data = calendar.get()
        filtered_calendar = data[data.advisor.isin(input.calendar_advisor_filter_())]
        ## if remarks is nan it creates an error when plotting (cannot create JSON object from nan)
        filtered_calendar['remarks'] = filtered_calendar.remarks.fillna(' ')

        ## Ensure the dataframe is valid
        if filtered_calendar.empty or filtered_calendar[['start_date', 'end_date']].isna().any().any():
            return None  # Return an empty plot or suitable default

        ## Handle calendar_date_range
        try:
            range_x_start, range_x_end = input.calendar_date_range_()
            ## transform date range into a datetime object to be used in the range_x of px.timeline
            range_x_start = datetime(range_x_start.year, range_x_start.month, range_x_start.day)
            range_x_end = datetime(range_x_end.year, range_x_end.month, range_x_end.day)
            assert range_x_start is not None and range_x_end is not None
        except (TypeError, AssertionError):
            range_x_start, range_x_end = None, None  # Default values if invalid

        ## ensure that single days events are represented with a visible width
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
        fig.update_traces(textposition='inside')
        fig.add_vline(x=datetime.today(), line_dash='dash', line_color='green')

        fig.update_xaxes(
            tickformat='%d-%b', dtick=86400000.0*5,
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

    ##
    ## Calendar - Data
    ##
    @render.data_frame
    def calendar_df():
        tmp = calendar.get()
        ## create the id columns to reference when editing
        tmp['id'] = tmp.index
        ## filter on the year
        data = tmp.copy() if input.table_year_select_() == 'All' else tmp[tmp.end_date.dt.year == int(input.table_year_select_())].copy()
        ## filter on the advisor
        data = data if input.table_advisor_select_() == 'All' else data[data.advisor==input.table_advisor_select_()]
        ## filter on the type
        data = data if input.table_type_select_() == 'All' else data[data.type==input.table_type_select_()]
        data['start_date'] = data.start_date.apply(hp.date_prettify)
        data['end_date'] = data.end_date.apply(hp.date_prettify)

        return render.DataGrid(
            data.sort_index(ascending=False),
            width='fit-content',
            # editable=get_editable_flag(),
            selection_mode='rows',# if get_editable_flag() else 'none',
        )

    @render.ui
    def edit_row():
        return ui.input_action_button(
            id='edit_row_',
            label='',
            # width='fit-content',
            class_='btn btn-outline-warning',
            icon=fa.icon_svg('pen-to-square'),
            # disabled= not get_editable_flag()
        )

    @render.ui
    def delete_from_calendar():
        return ui.input_action_button(
                    id='delete_from_calendar_',
                    label='',
                    # width='fit-content',
                    icon=fa.icon_svg('calendar-xmark'),
                    class_='btn btn-outline-danger',
                    # disabled=not get_editable_flag()
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
    @reactive.event(input.edit_row_)
    def _():
        ## get the indices of the selected rows in the current view (filtered or unfiltered)
        selected_rows = calendar_df.cell_selection()['rows'] ## this is a tuple

        ## check if you have at least one and only one row selected
        if len(selected_rows) != 1:
            ui.notification_show('Please select at least one and only one row for editing', type='error')
            return
        
        m = ui.modal(
            hp.EDIT_CALENDAR['advisor'],
            hp.EDIT_CALENDAR['type'],
            hp.EDIT_CALENDAR['start_date'],
            hp.EDIT_CALENDAR['end_date'],
            hp.EDIT_CALENDAR['remarks'],
            ui.div(
                ui.input_action_button('submit_edit_cal', 'Submit', class_='btn btn-primary'),
                class_='d-flex justify-content-end'
            ),
            easy_close=True,
            title='Edit Calendar Row',
        )
        
        ## make a dataframe of the current view (filter or unfiltered)
        tmp = pd.DataFrame(calendar_df.data_view())
        ## save the id of the one selected row (selected_rows is a tuple with only one element)
        id_in_selected = tmp.iloc[[int(selected_rows[0])]].id ## this is a series #set(tmp.iloc[[int(r) for r in selected_rows]].id)
        ## make a dataframe of the original (unfiltered) view
        original_df = calendar.get()#pd.DataFrame(calendar_df.data())
        ## identify the row to edit based on the id
        row_to_edit = original_df[original_df.id == id_in_selected.iloc[0]].iloc[0]

        ui.update_select('edit_advisor', selected=row_to_edit.advisor)
        ui.update_radio_buttons('edit_type', selected=row_to_edit.type)
        ui.update_date('edit_start_date', value=row_to_edit.start_date)
        ui.update_date('edit_end_date', value=row_to_edit.end_date)
        ui.update_text('edit_remarks', value='' if pd.isna(row_to_edit.remarks) else row_to_edit.remarks)

        ui.modal_show(m)

    @reactive.effect
    @reactive.event(input.submit_edit_cal)
    def _():
        ## get the indices of the selected rows in the current view (filtered or unfiltered)
        selected_rows = calendar_df.cell_selection()['rows'] ## this is a tuple
        ## make a dataframe of the current view (filter or unfiltered)
        tmp = pd.DataFrame(calendar_df.data_view())
        ## save the id of the one selected row (selected_rows is a tuple with only one element)
        id_in_selected = tmp.iloc[[int(selected_rows[0])]].id ## this is a series #set(tmp.iloc[[int(r) for r in selected_rows]].id)
        ## make a dataframe of the original (unfiltered) view
        original_df = calendar.get()#pd.DataFrame(calendar_df.data())
        ## identify the row to edit based on the id
        row_to_edit = original_df[original_df.id == id_in_selected.iloc[0]].iloc[0]

        try:
            updated_row = pd.DataFrame([{k: input[f'edit_{k}']() for k in hp.EDIT_CALENDAR.keys()}])## this is one-row dataframe
            ## Make sure that the new dataframe has the same columns order as the original one
            ## and that the dates are datetime objects
            updated_row = updated_row.reindex(columns=original_df.columns)
            updated_row['id'] = row_to_edit.id
            ## update the row in original df with the updated_row using the index
            updated_row.set_index('id', inplace=True)
            original_df.update(updated_row)

            calendar.set(original_df.drop('id', axis=1)) ## calendar reactive value does not have the id column
            ## save the calendar to excel
            hp.update_calendar(original_df)
            ui.notification_show(f'Updated entry for {row_to_edit.advisor}, thank you!', type='message')   
        except Exception:
            ui.notification_show(f'Oops, something went wrong. Retry!', type='error')
        
    @reactive.effect
    @reactive.event(input.delete_from_calendar_)
    def _():
        ## get the indices of the selected rows in the current view (filtered or unfiltered)
        selected_rows = calendar_df.cell_selection()['rows']
        tmp = pd.DataFrame(calendar_df.data_view())
        ## save the ids of selected rows into a set
        ids_in_selected = set(tmp.iloc[[int(r) for r in selected_rows]].id)

        if selected_rows:
            original_df = calendar_df.data()
            rows_to_drop = original_df[original_df.id.isin(ids_in_selected)].index
            updated_df = calendar.get().drop(rows_to_drop, axis=0)
            calendar.set(updated_df)
            ## save the calendar to excel
            hp.update_calendar(updated_df)
            ui.notification_show(f'Removing the following row(s): {[id for id in ids_in_selected]}', type='message')
        else:
            ui.notification_show(f'Please select one or more rows to be deleted', type='error')

    @reactive.effect
    @reactive.event(input.add_to_calendar)
    def _():
        m = ui.modal(
            hp.ADD_CALENDAR['advisor'],
            hp.ADD_CALENDAR['type'],
            hp.ADD_CALENDAR['start_date'],
            hp.ADD_CALENDAR['end_date'],
            hp.ADD_CALENDAR['remarks'],
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
        data = calendar.get()
        try:
            new_row = pd.DataFrame([{k: input[f'add_{k}']() for k in hp.ADD_CALENDAR.keys()}])
            ## Make sure that the new dataframe has the same columns order as the original one
            ## and that the dates are datetime objects
            new_row = new_row.reindex(columns=data.columns)
            new_row['start_date'] = pd.to_datetime(new_row.start_date, dayfirst=True, errors='raise', format='%d-%b-%Y')#'mixed')
            new_row['end_date'] = pd.to_datetime(new_row.end_date, dayfirst=True, errors='raise', format='%d-%b-%Y')#'mixed')
            ## add the new row to the existing dataframe and update the reactive value
            updated_cal = pd.concat([data, new_row], ignore_index=True)

            calendar.set(updated_cal)
            ## save the calendar to excel
            hp.update_calendar(updated_cal)
            ui.notification_show(f'New entry for {input.add_advisor()} added to the calendar, thank you!', type='message')   
        except Exception as e:
            ui.notification_show(f'Oops, something went wrong: {e}. Retry!', type='error')

    ##
    ## Calendar - Stats
    ##
    @render.ui
    def select_year():
        data = calendar.get()
        years = [yr for yr in data.end_date.dt.year]
        return ui.input_select(
                    id='select_year_',
                    label='',
                    choices=years,
                    width='100px'
                )

    @render_widget
    def plot_bar_days_bytype():
        year = input.select_year_()
        tmp = calendar.get()
        ## calculate the percentages on a copy of the dataframe so that the original is not changed
        data = hp.pcg_days_by_type(tmp.copy(), int(year))

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
    ### Country Calls ###
    ###
    @render.data_frame
    def calls_df():
        tmp = country_calls.get()
        ## create the id columns to reference when editing
        tmp['id'] = tmp.index
        data = tmp.copy()
        ## filter on the year
        data = data if input.call_year_select_() == 'All' else data[data.date.dt.year == int(input.call_year_select_())]
        ## filter on the country
        data = data if input.call_country_select_() == 'All' else data[data.country==input.call_country_select_()]
        # ## filter on the type
        # data = data if input.table_type_select_() == 'All' else data[data.type==input.table_type_select_()]
        
        data['date'] = data.date.apply(hp.date_prettify)

        return render.DataGrid(
            data.sort_index(ascending=False),
            width='fit-content',
            selection_mode='rows'
        )

    @render.ui
    def edit_call_row():
        return ui.input_action_button(
                id='edit_call_row_',
                label='',
                # width='fit-content',
                class_='btn btn-outline-warning',
                icon=fa.icon_svg('pen-to-square'),
                # disabled= not get_editable_flag()
            )
            
    @render.ui
    def delete_call():
        return ui.input_action_button(
                id='delete_call_',
                label='',
                # width='fit-content',
                icon=fa.icon_svg('calendar-xmark'),
                class_='btn btn-outline-danger',
                # disabled=not get_editable_flag()
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
            hp.ADD_CALL['date'],
            hp.ADD_CALL['country'],
            hp.ADD_CALL['sal_attendees'],
            hp.ADD_CALL['country_attendees'],
            hp.ADD_CALL['description'],
            ui.div(
                ui.input_action_button('submit_add_country_call', 'Submit', class_='btn btn-primary'),
                class_='d-flex justify-content-end'
            ),
            easy_close=True,
            title='New Country Call Entry',
        )
        ui.modal_show(m)

    @reactive.effect
    @reactive.event(input.submit_add_country_call)
    def _():
        data = country_calls.get()
        try:
            new_row = pd.DataFrame([{k: input[f'add_{k}_call']() for k in hp.ADD_CALL.keys()}])
            ## Make sure that the new dataframe has the same columns order as the original one
            ## and that the dates are datetime objects
            new_row = new_row.reindex(columns=data.columns)
            new_row['date'] = pd.to_datetime(new_row.date, dayfirst=True, errors='raise', format='%d-%b-%Y')
            ## add the new row to the existing dataframe and update the reactive value
            updated_country_calls = pd.concat([data, new_row], ignore_index=True)

            country_calls.set(updated_country_calls)
            ## save the calendar to excel
            hp.update_country_calls(updated_country_calls)
            ui.notification_show(f'New entry for {input.add_country_call()} added to the country calls registry, thank you!', type='message')   
        except Exception as e:
            ui.notification_show(f'Oops, something went wrong: {e}. Retry!', type='error')

    @reactive.effect
    @reactive.event(input.edit_call_row_)
    def _():
        ## get the indices of the selected rows in the current view (filtered or unfiltered)
        selected_rows = calls_df.cell_selection()['rows'] ## this is a tuple

        ## check if you have at least one and only one row selected
        if len(selected_rows) != 1:
            ui.notification_show('Please select at least one and only one row for editing', type='error')
            return
        
        m = ui.modal(
            hp.EDIT_CALL['date'],
            hp.EDIT_CALL['country'],
            hp.EDIT_CALL['sal_attendees'],
            hp.EDIT_CALL['country_attendees'],
            hp.EDIT_CALL['description'],
            ui.div(
                ui.input_action_button('submit_edit_country_call', 'Submit', class_='btn btn-primary'),
                class_='d-flex justify-content-end'
            ),
            easy_close=True,
            title='Edit Country Call Entry',
        )
        
        ## make a dataframe of the current view (filter or unfiltered)
        tmp = pd.DataFrame(calls_df.data_view())
        ## save the id of the one selected row (selected_rows is a tuple with only one element)
        id_in_selected = tmp.iloc[[int(selected_rows[0])]].id ## this is a series #set(tmp.iloc[[int(r) for r in selected_rows]].id)
        ## make a dataframe of the original (unfiltered) view
        original_df = country_calls.get()#pd.DataFrame(calendar_df.data())
        ## identify the row to edit based on the id
        row_to_edit = original_df[original_df.id == id_in_selected.iloc[0]].iloc[0]

        ui.update_date('edit_date_call', value=row_to_edit.date)
        ui.update_select('edit_country_call', selected=row_to_edit.country)
        ui.update_text('edit_sal_attendees_call', value=row_to_edit.sal_attendees)
        ui.update_text('edit_country_attendees_call', value=row_to_edit.country_attendees)
        ui.update_text_area('edit_description_call', value='' if pd.isna(row_to_edit.description) else row_to_edit.description)

        ui.modal_show(m)

    @reactive.effect
    @reactive.event(input.submit_edit_country_call)
    def _():
        ## get the indices of the selected rows in the current view (filtered or unfiltered)
        selected_rows = calls_df.cell_selection()['rows'] ## this is a tuple
        ## make a dataframe of the current view (filter or unfiltered)
        tmp = pd.DataFrame(calls_df.data_view())
        ## save the id of the one selected row (selected_rows is a tuple with only one element)
        id_in_selected = tmp.iloc[[int(selected_rows[0])]].id ## this is a series #set(tmp.iloc[[int(r) for r in selected_rows]].id)
        ## make a dataframe of the original (unfiltered) view
        original_df = country_calls.get()#pd.DataFrame(calendar_df.data())
        ## identify the row to edit based on the id
        row_to_edit = original_df[original_df.id == id_in_selected.iloc[0]].iloc[0]

        try:
            updated_row = pd.DataFrame([{k: input[f'edit_{k}_call']() for k in hp.EDIT_CALL.keys()}])## this is one-row dataframe
            ## Make sure that the new dataframe has the same columns order as the original one
            ## and that the dates are datetime objects
            updated_row = updated_row.reindex(columns=original_df.columns)
            updated_row['id'] = row_to_edit.id
            ## update the row in original df with the updated_row using the index
            updated_row.set_index('id', inplace=True)
            original_df.update(updated_row)

            country_calls.set(original_df.drop('id', axis=1)) ## country_calls reactive value does not have the id column
            ## save the calendar to excel
            hp.update_country_calls(original_df)
            ui.notification_show(f'Updated entry for {row_to_edit.country}, thank you!', type='message')   
        except Exception:
            ui.notification_show(f'Oops, something went wrong. Retry!', type='error')
        
    @reactive.effect
    @reactive.event(input.delete_call_)
    def _():
        ## get the indices of the selected rows in the current view (filtered or unfiltered)
        selected_rows = calls_df.cell_selection()['rows']
        tmp = pd.DataFrame(calls_df.data_view())
        ## save the ids of selected rows into a set
        ids_in_selected = set(tmp.iloc[[int(r) for r in selected_rows]].id)

        if selected_rows:
            original_df = calls_df.data()
            rows_to_drop = original_df[original_df.id.isin(ids_in_selected)].index
            updated_df = country_calls.get().drop(rows_to_drop, axis=0)
            country_calls.set(updated_df)
            ## save the calendar to excel
            hp.update_country_calls(updated_df)
            ui.notification_show(f'Removing the following row(s): {[id for id in ids_in_selected]}', type='message')
        else:
            ui.notification_show(f'Please select one or more rows to be deleted', type='error')

    @render.ui
    def call_year_select_2():
        data = country_calls.get()
        years = [int(yr) for yr in data.date.dt.year.unique()]
        years.append('All')
        return ui.input_select(
            id='call_year_select_2_',
            label='Filter by year:',
            choices = years,
            selected='All',
            width='150px'
        )

    @render_widget
    def plot_bar_calls_bycountry():
        year = input.call_year_select_2_()
        min_calls = int(input.min_calls_slider())
        tmp = country_calls.get()
        tmp = tmp.copy()
        ## group by country and filter by date
        if year == 'All':
            df = tmp
        else:
            df = tmp[tmp.date.dt.year == int(year)]
        data = df.groupby(['country']).agg({'sal_attendees':'count'}).reset_index().rename(columns={'sal_attendees':'no_calls'})

        fig = px.bar(
            data_frame = data[data.no_calls >= min_calls],
            x='no_calls',
            y='country',
            color='no_calls',
            labels={'country': '', 'no_calls': 'Total number of calls'}
        )

        fig.update_layout(yaxis={'categoryorder':'total ascending'})

        return fig

    @render.download()
    def download_db_xlsx():
        path = os.path.join(os.path.dirname(__file__), 'data', 'database.xlsx')
        return path


app = App(app_ui, server)
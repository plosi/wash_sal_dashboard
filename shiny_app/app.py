from shiny import App, render, reactive, ui
from shinywidgets import output_widget, render_widget, render_plotly

from pathlib import Path
from datetime import datetime, timedelta
import faicons as fa
import pandas as pd
import plotly.express as px

import helpers as hp
from helpers import advisors, countries#, wash_list#, types, calendar

app_dir = Path(__file__).parent

calendar = reactive.Value()
wash_list = reactive.Value()

calendar.set(hp.import_calendar())
wash_list.set(hp.import_wash_list())

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
                        ui.markdown('Controls'),
                        ui.row(
                            ui.column(
                                6,
                                ui.input_action_button(
                                    id='add_to_calendar',
                                    label='Add',
                                    icon=fa.icon_svg('calendar-plus'),
                                    class_='btn btn-outline-success'
                                ),
                            ),
                            ui.column(
                                6,
                                ui.input_switch(
                                    id='edit_calendar',
                                    label='Enable edit',
                                    value=False
                                ),
                            ),
                        ),
                        ui.row(
                            ui.column(6),
                            ui.column(6,ui.output_ui('delete_from_calendar')),
                        ),
                        ui.row(
                            ui.column(6),
                            ui.column(6,ui.output_ui('edit_row')),
                        ),
                        # ui.row(
                        #     ui.column(6),
                        #     ui.column(6,ui.output_ui('save_changes')),
                        # ),
                        # ui.markdown('Filters'),
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
                col_widths=(8,4)
            ),
        ),
    ),

    ## Country Calls Panel
    ui.nav_panel(
        'Country Calls',
        ui.markdown('hello')
    ),

    ## Capacity Building Panel
    ui.nav_panel(
        'Capacity Building',
        ui.markdown('hello again')
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
        ## TO DO: one day activity doesn't display well
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
            selection_mode='rows' if get_editable_flag() else 'none',
        )

    @render.ui
    def edit_row():
        return ui.input_action_button(
            id='edit_row_',
            label='',
            # width='fit-content',
            class_='btn btn-outline-danger',
            icon=fa.icon_svg('pen-to-square'),
            disabled= not get_editable_flag()
        )

    @render.ui
    def delete_from_calendar():
        return ui.input_action_button(
                    id='delete_from_calendar_',
                    label='',
                    # width='fit-content',
                    icon=fa.icon_svg('calendar-xmark'),
                    class_='btn btn-outline-danger',
                    disabled=not get_editable_flag()
                )

    # @render.ui
    # def save_changes():
    #     return ui.input_action_button(
    #         id='save_changes_',
    #         label='',
    #         # width='fit-content',
    #         class_='btn btn-outline-success',
    #         icon=fa.icon_svg('floppy-disk'),
    #         disabled= not get_editable_flag()
    #     )
    
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
            hp.EDIT_CAL['advisor'],
            hp.EDIT_CAL['type'],
            hp.EDIT_CAL['start_date'],
            hp.EDIT_CAL['end_date'],
            hp.EDIT_CAL['remarks'],
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
            updated_row = pd.DataFrame([{k: input[f'edit_{k}']() for k in hp.EDIT_CAL.keys()}])## this is one-row dataframe
            ## Make sure that the new dataframe has the same columns order as the original one
            ## and that the dates are datetime objects
            updated_row = updated_row.reindex(columns=original_df.columns)
            updated_row['id'] = row_to_edit.id
            ## update the row in original df with the updated_row using the index
            updated_row.set_index('id', inplace=True)
            original_df.update(updated_row)

            calendar.set(original_df.drop('id', axis=1)) ## calendar reactive value does not have the id column
            ## save the calendar to excel
            hp.update_calendar(original_df.drop('id', axis=1))
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
    @reactive.event(input.save_changes_)
    def _():
        try:
            data = calendar.get().drop(['id'], axis=1)
            hp.update_calendar(data)
            ui.notification_show('Your changes have been saved to file.', type='message')
        except Exception as e:
            ui.notification_show(f'Something went wrong: {e}', type='error')
        
    @reactive.calc
    def get_editable_flag():
        return input.edit_calendar()
    
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
        data = calendar.get()
        try:
            new_row = pd.DataFrame([{k: input[f'add_{k}']() for k in hp.ADD_CAL.keys()}])
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
        except Exception:
            ui.notification_show(f'Oops, something went wrong. Retry!', type='error')

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
            barmode='group',
            labels={'type': '', 'advisor':'', 'total_busdays': 'Total business days'}
        )

        return fig

    ###
    ### Country Allocation ###
    ###
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


    # @render.download(filename='updated_cal.xlsx')
    # def save_calendar():
    #     yield calendar_df.data_view().to_excel(excel_writer='openpyxl', index=False, sheet_name='calendar')


app = App(app_ui, server)
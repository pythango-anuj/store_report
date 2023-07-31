import csv
import random
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apis.models import PollDetails, BusinessHoursOfStores, StoreTimezone, Report, CSV_Report
from django.utils import timezone
from datetime import timedelta, datetime
import pytz
import csv
from io import StringIO
from django.core.files import File

store_report = dict()

def convert_to_utc(local_time, timezone_str):
    local_timezone = pytz.timezone(timezone_str)
    local_datetime = datetime.combine(timezone.now().date(), local_time)
    local_datetime = local_timezone.localize(local_datetime)
    utc_datetime = local_datetime.astimezone(pytz.utc)
    return utc_datetime

def downtime_last_hour(store_id):
    # Get the current datetime in the default timezone (settings.TIME_ZONE)
    current_datetime = timezone.now()

    # Get the datetime one hour ago from the current datetime
    one_hour_ago = current_datetime - timedelta(hours=1)

    # Get polls for the last hour
    polls_last_hour = PollDetails.objects.filter(timestamp_utc__gte=one_hour_ago)

    # Get the current day of the week (Monday is 0, Sunday is 6)
    current_day_of_week = current_datetime.weekday()

    # List business hours of whole week for a store
    store = BusinessHoursOfStores.objects.all().filter(store_id=store_id)

    store_today = store.filter(dayOfWeek=str(current_day_of_week))
    if len(store_today)>0:
        # Local timing of store:
        start_time_local_str = str(store_today[0].start_time_local)
        end_time_local_str = str(store_today[0].end_time_local)

        # UTC Timing of stores:

        #Obtain the local timezone strings for starttime and closetime
        try:
            local_timezone_str = StoreTimezone.objects.all().get(store_id=store_id).timezone_str
        except:
            local_timezone_str="America/Chicago"

        # Convert start time and end time to UTC using the separate functions
        start_time_local = datetime.strptime(start_time_local_str, '%H:%M:%S').time()
        end_time_local = datetime.strptime(end_time_local_str, '%H:%M:%S').time()

        # Convert local time strings to datetime objects
        start_time_utc = convert_to_utc(start_time_local, local_timezone_str)
        end_time_utc = convert_to_utc(end_time_local, local_timezone_str)

        effective_polls_last_hour = polls_last_hour.filter(timestamp_utc__range=(start_time_utc, end_time_utc))
        add = False
        offtime_last_hour=0
        for i in effective_polls_last_hour:
            if effective_polls_last_hour[i].status=="inactive":
                if add:
                    offtime_last_hour+=(effective_polls_last_hour[i].timestamp_utc - effective_polls_last_hour[i-1].timestamp_utc).total_seconds()/60
                add=True
            else:
                add=False
        return offtime_last_hour
    return 0
    

def downtime_last_day(store_id):
    # Get the current datetime in the default timezone (settings.TIME_ZONE)
    current_datetime = timezone.now()

    # Get the datetime one day ago from the current datetime
    one_day_ago = current_datetime - timedelta(days=1)

    # Get polls for the last day
    polls_last_day = PollDetails.objects.filter(timestamp_utc__gte=one_day_ago)

    # Get the current day of the week (Monday is 0, Sunday is 6)
    current_day_of_week = current_datetime.weekday()
    yesterday = one_day_ago.weekday()

    # List business hours of whole week for a store
    store = BusinessHoursOfStores.objects.all().filter(store_id=store_id)

    store_today = store.filter(dayOfWeek=str(yesterday))
    if len(store_today)>0:
        # Local timing of store:
        start_time_local_str = str(store_today[0].start_time_local)
        end_time_local_str = str(store_today[0].end_time_local)

        # UTC Timing of stores:

        #Obtain the local timezone strings for starttime and closetime
        try:
            local_timezone_str = StoreTimezone.objects.all().get(store_id=store_id).timezone_str
        except:
            local_timezone_str="America/Chicago"

        # Convert start time and end time to UTC using the separate functions
        start_time_local = datetime.strptime(start_time_local_str, '%H:%M:%S').time()
        end_time_local = datetime.strptime(end_time_local_str, '%H:%M:%S').time()

        # Convert local time strings to datetime objects
        start_time_utc = convert_to_utc(start_time_local, local_timezone_str)
        end_time_utc = convert_to_utc(end_time_local, local_timezone_str)

        effective_polls_last_day = polls_last_day.filter(timestamp_utc__range=(start_time_utc, end_time_utc))
        add = False
        offtime_last_day=0
        active_time = (end_time_utc - start_time_utc).total_seconds()/3600
        for i in effective_polls_last_day:
            if effective_polls_last_day[i].status=="inactive":
                if add:
                    offtime_last_day+=(effective_polls_last_day[i].timestamp_utc - effective_polls_last_day[i-1].timestamp_utc).total_seconds()/3600
                add=True
            else:
                add=False
        return {'offtime_last_day': offtime_last_day, 'active_time': active_time}
    return {'offtime_last_day': 0, 'active_time': 0}
    
def downtime_last_week(store_id):
    # Get the current datetime in the default timezone (settings.TIME_ZONE)
    current_datetime = timezone.now()

    # Calculate the date for last week's starting day (7 days ago from the current date)
    last_week_start = current_datetime - timedelta(days=current_datetime.weekday() + 7)

    # Calculate the date for last week's ending day (1 day before the starting day of this week)
    last_week_end = last_week_start + timedelta(days=6)

    # Iterate over the days of last week
    xday_datetime = last_week_start

    offtime_last_week=0
    active_time=0

    while xday_datetime <= last_week_end:
        xday_datetime += timedelta(days=1)

        # Get polls for the last day
        polls_x_day = PollDetails.objects.filter(timestamp_utc__gte=xday_datetime)

        # Get the current day of the week (Monday is 0, Sunday is 6)
        x_day_of_week = xday_datetime.weekday()

        # List business hours of whole week for a store
        store = BusinessHoursOfStores.objects.all().filter(store_id=store_id)

        store_today = store.filter(dayOfWeek=str(x_day_of_week))
        if len(store_today)>0:
            # Local timing of store:
            start_time_local_str = str(store_today[0].start_time_local)
            end_time_local_str = str(store_today[0].end_time_local)

            # UTC Timing of stores:

            #Obtain the local timezone strings for starttime and closetime
            try:
                local_timezone_str = StoreTimezone.objects.all().get(store_id=store_id).timezone_str
            except:
                local_timezone_str="America/Chicago"

            # Convert start time and end time to UTC using the separate functions
            start_time_local = datetime.strptime(start_time_local_str, '%H:%M:%S').time()
            end_time_local = datetime.strptime(end_time_local_str, '%H:%M:%S').time()

            # Convert local time strings to datetime objects
            start_time_utc = convert_to_utc(start_time_local, local_timezone_str)
            end_time_utc = convert_to_utc(end_time_local, local_timezone_str)

            active_time+=(end_time_utc-start_time_utc).total_seconds()/3600
            effective_polls_x_day = polls_x_day.filter(timestamp_utc__range=(start_time_utc, end_time_utc))
            add = False
            offtime_x_day=0
            for i in effective_polls_x_day:
                if effective_polls_x_day[i].status=="inactive":
                    if add:
                        offtime_x_day+=((effective_polls_x_day[i].timestamp_utc - effective_polls_x_day[i-1].timestamp_utc).total_seconds())/3600
                    add=True
                else:
                    add=False
            offtime_last_week+=offtime_x_day
    return {'offtime_last_week': offtime_last_week, 'active_time': active_time}



def generate_and_save_csv(report_id):
    # Assuming you have the report data as a dictionary
    csv_data = "store_id,uptime_last_hour,uptime_last_day,uptime_last_week,downtime_last_hour,downtime_last_day,downtime_last_week\n"
    reports = Report.objects.all()
    for report_data in reports:
        csv_data += f"{report_data['store_id']},{report_data['uptime_last_hour']},{report_data['uptime_last_day']},{report_data['uptime_last_week']},{report_data['downtime_last_hour']},{report_data['downtime_last_day']},{report_data['downtime_last_week']}\n"

    # Create a StringIO object to simulate a file
    csv_file = StringIO(csv_data)
    
    # Save the CSV file to the FileField
    csv_report = CSV_Report()
    csv_report.report_id = report_id
    csv_report.csv_data.save('report_data.csv', File(csv_file))
    csv_report.save()

    return csv_report


@csrf_exempt
@api_view(['POST'])
def trigger_report(request):
    # List the store ids
    Report.objects.all().delete()
    stores = BusinessHoursOfStores.objects.all()
    for store in stores:
        if store.store_id not in store_report:
            store_report[store.store_id] = 0
    
    # Prepare report for each and every store_id
    for id in store_report:
        report = Report()
        report.store_id =id

        times_last_our = downtime_last_hour(id)
        report.downtime_last_hour = times_last_our
        report.uptime_last_hour = 60-int(times_last_our)

        times_last_day = downtime_last_day(id)
        report.downtime_last_day = times_last_day['offtime_last_day']
        report.uptime_last_day = times_last_day['active_time']

        times_last_week = downtime_last_week(id)
        report.downtime_last_week = times_last_week['offtime_last_week']
        report.uptime_last_week = times_last_week['active_time']

        report.save()

    report_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10))
    generate_and_save_csv(report_id)
    return Response({'report_id': report_id})


@api_view(['GET'])
def get_report(request, report_id):
    csv_report = get_object_or_404(CSV_Report,report_id=report_id)

    if csv_report.is_complete:
        response = HttpResponse(csv_report.csv, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report_id}.csv"'
        return response
    else:
        # If report generation is not complete, return "Running"
        return Response({'status': 'Running'})
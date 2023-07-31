from typing import Any
from django.db import models
from django.utils import timezone



STATUS_CHOICES = (
    ("active", "active"),
    ("inactive", "inactive")
)



class PollDetails(models.Model):
    store_id = models.IntegerField()
    timestamp_utc= models.DateTimeField()
    status = models.CharField(choices=STATUS_CHOICES, max_length=10)

    def __str__(self) -> str:
        return str(self.store_id) + "Poll"
    


DAYS_OF_WEEK = (
    ("0", "Monday"),
    ("1", "Tuesday"),
    ("2", "Wednesday"),
    ("3", "Thursday"),
    ("4", "Friday"),
    ("5", "Saturday"),
    ("6", "Sunday")
)



class BusinessHoursOfStores(models.Model):
    store_id = models.IntegerField()
    dayOfWeek = models.CharField(choices=DAYS_OF_WEEK, max_length=10)
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()

    def __str__(self) -> str:
        return str(self.store_id) + "BusinessHours"
    


class StoreTimezone(models.Model):
    store_id = models.IntegerField()
    timezone_str = models.CharField(max_length=50)

    def __str__(self) -> str:
        return str(self.store_id) + "TimeZone"



class Report(models.Model):
    store_id = models.BigIntegerField()
    uptime_last_hour = models.IntegerField()
    uptime_last_day = models.IntegerField()
    uptime_last_week = models.IntegerField()
    downtime_last_hour = models.IntegerField()
    downtime_last_day = models.IntegerField()
    downtime_last_week = models.IntegerField()

    def __str__(self) -> str:
        return str(self.store_id) + "Report"
    

class CSV_Report(models.Model):
    report_id = models.CharField(max_length=10)
    csv_report = models.FileField(upload_to='report_csv/', null=True)
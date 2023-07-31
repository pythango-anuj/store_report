from django.contrib import admin
from .models import BusinessHoursOfStores, StoreTimezone, Report, PollDetails, CSV_Report



admin.site.register(PollDetails)
admin.site.register(BusinessHoursOfStores)
admin.site.register(StoreTimezone)
admin.site.register(Report)
admin.site.register(CSV_Report)

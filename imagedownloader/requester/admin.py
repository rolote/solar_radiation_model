from django.contrib import admin
from requester.models import *

class AreaAdmin(admin.ModelAdmin):
	list_display = [ 'name', 'north_latitude', 'south_latitude', 'east_longitude', 'west_longitude']

class UTCTimeRangeAdmin(admin.ModelAdmin):
	list_display = ['begin', 'end']

class SatelliteAdmin(admin.ModelAdmin):
	list_display = [ 'name', 'request_server' ]

class ChannelAdmin(admin.ModelAdmin):
	list_display = [ 'name', 'satellite' ]

class WebServerAccountAdmin(admin.ModelAdmin):
	list_display = ['url', 'username' ]

class EmailAccountAdmin(admin.ModelAdmin):
	list_display = [ 'username', 'hostname', 'port' ]

class FTPServerAccountAdmin(admin.ModelAdmin):
	list_display = [ 'hostname', 'username' ]

class OrderAdmin(admin.ModelAdmin):
	list_display = [ 'identification', 'downloaded', 'year', 'julian_day', 'progress', 'downloaded_porcentage', 'total_time', 'average_speed', 'download_speed' ]
	search_fields = ['identification']

class RequestAdmin(admin.ModelAdmin):
	list_display = [ 'identification', 'begin', 'end', 'progress', 'downloaded_porcentage', 'total_time' ]

class FileAdmin(admin.ModelAdmin):
	list_display = [ 'downloaded', 'downloaded_porcentage', 'progress', 'download_speed', 'filename', 'size', 'begin_download' ]
	list_filter = ['begin_download', 'end_download', 'size' ]
	search_fields = ['begin_download', 'end_download', 'size', 'localname']

class AutomaticDownloadAdmin(admin.ModelAdmin):
	list_display = [ 'paused','title', 'progress', 'time_range', 'area', 'root_path', 'total_time', 'estimated_time', 'average_time' ]

admin.site.register(Area, AreaAdmin)
admin.site.register(UTCTimeRange, UTCTimeRangeAdmin)
admin.site.register(GOESRequest, RequestAdmin)
admin.site.register(WebServerAccount, WebServerAccountAdmin)
admin.site.register(Satellite, SatelliteAdmin)
admin.site.register(Channel, ChannelAdmin)
admin.site.register(EmailAccount, EmailAccountAdmin)
admin.site.register(FTPServerAccount, FTPServerAccountAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(AutomaticDownload, AutomaticDownloadAdmin)

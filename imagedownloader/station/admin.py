from django.contrib import admin
from station.models import *
from django.forms import ModelForm


class BrandAdmin(admin.ModelAdmin):
    list_display = [ 'name' ]

class OpticFilterAdmin(admin.ModelAdmin):
    list_display = [ 'name', 'description' ]

class ProductAdmin(admin.ModelAdmin):
    list_display = [ 'name', 'brand', ]

class SensorAdmin(admin.ModelAdmin):
    list_display = [ 'serial_number', 'optic_filter', 'product' ]

class ConfigurationAdmin(admin.ModelAdmin):
    list_display = [ 'datetime', 'frequency', 'frequency_save', 'calibration_value', 'sensor', 'position' ]

class MeasureAdmin(admin.ModelAdmin):
    list_display = [ 'value', 'date', 'configuration' ]

class StationAdmin(admin.ModelAdmin):
    list_display = [ 'name', 'coordinates' ]

class PositionAdmin(admin.ModelAdmin):
    list_display = [ 'latitude', 'longitude' ]

class DataloggerAdmin(admin.ModelAdmin):
    list_display = [ 'label' ]

class ChannelAdmin(admin.ModelAdmin):
    list_display = [ 'name', 'datalogger']

class StaticConfigurationAdmin(admin.ModelAdmin):
    list_display = [ 'datetime', 'frequency', 'frequency_save', 'calibration_value', 'sensor', 'position' ]

class DirectAdmin(admin.ModelAdmin):
    list_display = [ '' ]

class GlobalAdmin(admin.ModelAdmin):
    list_display = [ '' ]

class DifuseAdmin(admin.ModelAdmin):
    list_display = [ 'shadow_ball' ]

admin.site.register(Brand, BrandAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(OpticFilter, OpticFilterAdmin)
admin.site.register(Sensor, SensorAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(Datalogger, DataloggerAdmin)
admin.site.register(Channel, ChannelAdmin)
admin.site.register(Diffuse, StaticConfigurationAdmin)
admin.site.register(Global, StaticConfigurationAdmin)
admin.site.register(Direct, ConfigurationAdmin)

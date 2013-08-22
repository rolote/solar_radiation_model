from django.contrib import admin
from plumbing.models import *
from django.forms import ModelForm

class ProcessInlineForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(ProcessInlineForm, self).__init__(*args, **kwargs)
		self.fields['process'].queryset = Process.objects.all() 

class ProcessOrderInline(admin.TabularInline):
	form = ProcessInlineForm
	model = ProcessOrder
	fk_name = 'complex_process'
	extra = 0 # how many rows to show
	ordering = ["position",]
	

class ComplexProcessAdmin(admin.ModelAdmin):
	list_display = [ 'name', 'description']
	inlines = [ProcessOrderInline]
	search_fields = ['name', 'description', ]

class ProgramAdmin(admin.ModelAdmin):
	list_display = [ 'name', 'description', 'automatic_download']
	inlines = [ProcessOrderInline]
	search_fields = ['name', 'description', ]

class CompactAdmin(admin.ModelAdmin):
	list_display= [ 'name', 'description', 'extension']

class CollectTimedAdmin(admin.ModelAdmin):
	list_display = [ 'name', 'description', 'monthly']

class CollectChannelAdmin(admin.ModelAdmin):
	list_display = [ 'name', 'description' ]

class FilterAdmin(admin.ModelAdmin):
	list_display = [ 'name', 'description']

class FilterSolarElevationAdmin(admin.ModelAdmin):
	list_display = [ 'name', 'description', 'minimum']

class TransformCountsToRadiationAdmin(admin.ModelAdmin):
	list_display = [ 'counts_shift', 'calibrated_coefficient', 'space_measurement']

admin.site.register(TransformCountsToRadiation, TransformCountsToRadiationAdmin)
admin.site.register(ComplexProcess, ComplexProcessAdmin)
admin.site.register(Compact, CompactAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(FilterTimed, FilterAdmin)
admin.site.register(FilterChannel, FilterAdmin)
admin.site.register(CollectTimed, CollectTimedAdmin)
admin.site.register(CollectChannel, CollectChannelAdmin)
admin.site.register(FilterSolarElevation, FilterSolarElevationAdmin)

from django.contrib import admin
from bridge.models.models import *
# Register your models here.
admin.site.register(EmailMessage)
admin.site.register(MessageTemplates)



class ErrorLoggerModelAdmin(admin.ModelAdmin):
    list_display = ('subject','message','responseDump','errorType','user','date_logged')


admin.site.register(ErrorLoggerModel, ErrorLoggerModelAdmin)


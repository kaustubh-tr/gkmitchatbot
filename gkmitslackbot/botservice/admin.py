from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register([employee, skill, emp_skill, project, emp_project])

# Adding Timestamp
class ChatHistoryAdmin(admin.ModelAdmin):
    readonly_fields = ('timestamp',)
    list_display = ('id', 'employee_id', 'message', 'response', 'timestamp') 

admin.site.register(chat_history, ChatHistoryAdmin)
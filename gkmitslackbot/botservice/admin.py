from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register([Employee, Skill, EmpSkill, Project, EmpProject])

# Adding Timestamp
class ChatHistoryAdmin(admin.ModelAdmin):
    readonly_fields = ('timestamp',)
    list_display = ('id', 'employee_id', 'message', 'response', 'timestamp') 

admin.site.register(ChatHistory, ChatHistoryAdmin)
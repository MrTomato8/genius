from django.contrib import admin
from django.db.models import get_model


from .models import Job, Task, Stage, CommonTaskDescription


class JobAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'creator')

class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'job', 'creator', 'assigned_to')

class StageAdmin(admin.ModelAdmin):
    list_display = ('name', 'related_status', 'is_default')

admin.site.register(Job, JobAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Stage, StageAdmin)

admin.site.register(CommonTaskDescription)
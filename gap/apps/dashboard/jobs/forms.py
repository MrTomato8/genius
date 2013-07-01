from django import forms

from .models import Job, Stage, Task

class JobForm(forms.ModelForm):

    stages = forms.ModelMultipleChoiceField(queryset=Stage.objects.filter(is_default=True),
        help_text="<a href='/dashboard/jobs/stages/create/'>Create a new Stage</a>")
 

    class Meta:
        model = Job
        fields = ('name', 'stages')

class TaskForm(forms.ModelForm):
   
    class Meta:
        model = Task
        fields = ('job', 'name', 'assigned_to', 'description', 'priority', 'start_date', 'end_date')

class StageForm(forms.ModelForm):
   

    class Meta:
        model = Stage
        fields = ('name', 'related_status', 'is_default')
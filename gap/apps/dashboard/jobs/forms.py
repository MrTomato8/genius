from django import forms

from .models import Job, Stage, Task

class JobForm(forms.ModelForm):

    stages = forms.ModelMultipleChoiceField(queryset=Stage.objects.filter(is_default=True),
        help_text="<a href='/dashboard/jobs/stages/create/'>Create a new Stage</a>")
 

    class Meta:
        model = Job
        fields = ('order', 'name', 'stages')

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs and kwargs['instance']:                
            initial = kwargs.setdefault('initial', {})
            initial['stages'] = [t.pk for t in kwargs['instance'].stage_set.all()]
        else:
            initial['stages'] = Stage.objects.filter(is_default=True)

        forms.ModelForm.__init__(self, *args, **kwargs)

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, False)
        old_save_m2m = self.save_m2m
        
        def save_m2m():
           old_save_m2m()
           instance.stage_set.clear()
           for stage in self.cleaned_data['stages']:
               instance.stage_set.add(stage)
        self.save_m2m = save_m2m

        if commit:
            instance.save()
            self.save_m2m()

        return instance

class TaskForm(forms.ModelForm):
   
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        initial = kwargs.setdefault('initial', {})
        self.fields['stage'].queryset = Stage.objects.filter(is_default=True)

        if 'job' in initial.keys():    
            self.fields['stage'].queryset = initial['job'].stage_set.all() or\
                                            self.fields['stage'].queryset
        

    class Meta:
        model = Task
        fields = ('job', 'name', 'stage', 'assigned_to', 'description', 'priority', 'start_date', 'end_date')

class StageForm(forms.ModelForm):
   
    class Meta:
        model = Stage
        fields = ('name', 'related_status', 'is_default')
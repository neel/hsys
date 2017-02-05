from django import forms
from registration.forms import RegistrationForm
from identity.models import *

class LoginForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput())
    
    class Meta:
        model = HmsUser
        fields = ('username', 'password')

class ActivityForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ActivityForm, self).__init__(*args, **kwargs)
        
        self.fields['status'].error_messages = {
            'required': 'Status not mentioned'
        }
        self.fields['note'].error_messages = {
            'required': 'Please Leave a note while changing the status'
        }
    
    class Meta:
        model = Activity
        fields = ['note', 'status']

class PatientRegistrationForm(RegistrationForm):
    class Meta:
        model = Patient
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'dob', 'sex', 'address', )
        exclude = ('password', 'last_login', 'is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions', 'date_joined',)
        
class DoctorRegistrationForm(RegistrationForm):
    class Meta:
        model = Doctor
        exclude = ('password', 'last_login', 'is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions', 'date_joined',)
        
class OperatorRegistrationForm(RegistrationForm):
    class Meta:
        model = Operator
        exclude = ('password', 'last_login', 'is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions', 'date_joined',)

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = HmsUser
        fields = '__all__'
        
class AppointmentCreationForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('doctor', 'schedule', 'note')
        
class RandomVisitCreationForm(forms.ModelForm):
    class Meta:
        model = RandomVisit
        fields = ('patient', 'subject', 'body', 'refers_to')
        
class NegotiationForm(forms.ModelForm):
    class Meta:
        model = Negotiation
        fields = ('appointment', 'status', 'when', 'note')
        
class TaskCreationForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('admission', 'when', 'subject', 'body')

from django.http import HttpResponse, Http404
from identity.models import Organization, Patient, Doctor, Admission, Task
from django.views.generic import TemplateView
from django.template import RequestContext, loader
from django.shortcuts import render
import datetime, json
import random
import pdb

def DoctorPanel(request, doctor):
    return render(request, 'panel/doctor.html', {
        'request': request,
        'doctor': doctor
    })

def OperatorPanel(request, operator):
    return render(request, 'panel/operator.html', {
        'request': request,
        'operator': operator
    })

def PatientPanel(request, patient):
    return render(request, 'panel/patient.html', {
        'request': request,
        'patient': patient
    })

def PatientsPanel(request, patients):
    return render(request, 'panel/patients.html', {
        'request': request,
        'patients': patients
    })

def AppointmentCreationPanel(request, form):
    return render(request, 'panel/appointment-create.html', {
        'request': request,
        'form': form
    })

def RandomStoryCreationPanel(request, form):
    return render(request, 'panel/story-random-create.html', {
        'request': request,
        'form': form
    })

def AppointmentsPanel(request, appointments):
    if request.user.is_anonymous():
        user = request.user
    else:
        if hasattr(request.user, 'doctor'):
            user = request.user.doctor
        elif hasattr(request.user, 'patient'):
            user = request.user.patient
        elif hasattr(request.user, 'operator'):
            user = request.user.operator
        else:
            user = request.user
    
    # pdb.set_trace()
    return render(request, 'panel/appointments.html', {
        'request': request,
        'appointments': appointments,
        'user': user
    })

def MiniStoriesPanel(request, stories):
    return render(request, 'panel/ministories.html', {
        'request': request,
        'stories': stories
    })

def AdmissionsPanel(request, admissions):
    return render(request, 'panel/admissions.html', {
        'request': request,
        'admissions': admissions
    })

def TaskCreationPanel(request, form, admission):
    return render(request, 'panel/task-create.html', {
        'request': request,
        'form': form,
        'admission': admission.id
    })

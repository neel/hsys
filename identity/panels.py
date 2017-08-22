from django.http import HttpResponse, Http404
from identity.models import Organization, Patient, Doctor, Admission, Task
from identity.access import MessageAccess
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

def MiniStoriesPanel(request, stories, nstories, owner):
    return render(request, 'panel/ministories.html', {
        'request': request,
        'stories': stories,
        'nstories': nstories,
        'nstories': nstories,
        'owner': owner
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

def ChatPanel(request):
    messages = MessageAccess().all(request.user)
    latest_id = messages.latest('id').id if len(messages) else 0
    return render(request, 'panel/chat.html', {
        'request': request,
        'latest': latest_id
    })

def PrescriptionCreationPanel(request):
    return render(request, 'panel/prescription-creator.html', {
        'request': request
    })
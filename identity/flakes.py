from django.http import HttpResponse, Http404
from identity.models import Organization, Patient, Doctor, Bed, Admission, Task
from django.views.generic import TemplateView
from django.template import RequestContext, loader
from django.shortcuts import render
import datetime, json
import random

def AppointmentsFlake(request, user, appointments):
    return render(request, 'sprite/_appointments.html', {
        'request': request,
        'user': user,
        'appointments': appointments
    })

def AdmissionsFlake(request, user, admissions):
    return render(request, 'sprite/_admissions.html', {
        'request': request,
        'user': user,
        'admissions': admissions
    })

def StoriesFlake(request, user, stories):
    return render(request, 'sprite/_stories.html', {
        'request': request,
        'user': user,
        'stories': stories
    })

def TasksFlake(request, user, tasks):
    return render(request, 'sprite/_tasks.html', {
        'request': request,
        'user': user,
        'tasks': tasks
    })

def ActivitiesFlake(request, user, tasks):
    return render(request, 'sprite/_activities.html', {
        'request': request,
        'user': user,
        'activities': activities
    })
from django.http import HttpResponse, Http404
from identity.models import Organization, Patient, Doctor, Bed, Admission, Task
from django.views.generic import TemplateView
from django.template import RequestContext, loader
from django.shortcuts import render
import datetime, json
import random
import logging

def DoctorSprite(request, doctor):
    return render(request, 'sprite/doctor.html', {
        'request': request,
        'doctor': doctor
    })

def DoctorFlatSprite(request, doctor):
    return render(request, 'sprite/doctor-flat.html', {
        'request': request,
        'doctor': doctor
    })

def PatientSprite(request, patient):
    return render(request, 'sprite/patient.html', {
        'request': request,
        'patient': patient
    })
    
def OrganizationSprite(request, organization):
    return render(request, 'sprite/organization.html', {
        'request': request,
        'organization': organization
    })

def BedSprite(request, bed):
    return render(request, 'sprite/bed.html', {
        'request': request,
        'bed': bed
    })

def TaskSprite(request, task):
    return render(request, 'sprite/task.html', {
        'request': request,
        'task': task
    })

def ActivitySprite(request, activity):    
    return render(request, 'sprite/activity.html', {
        'request': request,
        'activity': activity,
        'who': activity.actor()
    })

def AppointmentSprite(request, appointment):
    return render(request, 'sprite/appointment.html', {
        'request': request,
        'appointment': appointment
    })

def NegotiationSprite(request, negotiation):
    try:
        user = negotiation.who.doctor
    except Doctor.DoesNotExist:
        try:
            user = negotiation.who.patient
        except Patient.DoesNotExist:
            try:
                user = negotiation.who.operator
            except Operator.DoesNotExist:
                user = negotiation.who
    
    return render(request, 'sprite/negotiation.html', {
        'request': request,
        'negotiation': negotiation,
        'who': user
    })

def NoticeSprite(request, notice):
    return render(request, 'sprite/notice.html', {
        'request': request,
        'notice': notice
    })

def MiniStorySprite(request, story):
    return render(request, 'sprite/story-mini.html', {
        'request': request,
        'story': story
    })

def StoryCardSprite(request, story):
    return render(request, 'sprite/story-card.html', {
        'request': request,
        'story': story
    })

def AdmissionSprite(request, admission):
    return render(request, 'sprite/admission.html', {
        'request': request,
        'admission': admission
    })

def _ActivitiesSprite(request, activities):    
    return render(request, 'sprite/_activities.html', {
        'request': request,
        'activities': activities
    })

def StoryViewerSprite(request, story):
    story.body = json.loads(story.body)
    print(story.media)
    if(story.media and len(story.media) > 0):
        story.media = json.loads(story.media)
    return render(request, 'sprite/story-viewer.html', {
        'request': request,
        'story': story
    })

def PrescriptionViewerSprite(request, story, complaints, prescriptions):
    return render(request, 'sprite/prescription-viewer.html', {
        'request': request,
        'story': story,
        'complaints': complaints,
        'prescriptions': prescriptions
    })
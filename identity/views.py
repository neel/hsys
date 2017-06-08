from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied
from django.template import RequestContext, loader
from django.views.generic.base import View
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.template import Context, Template
import datetime, json
import random
from identity.models import *
from identity.forms import *
from identity.sprites import *
from identity.panels import *
from identity.constructs import *
from identity.access import *
import pdb

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            encoded_object = ','.join(str(i) for i in list(obj.timetuple())[0:6])
        else:
            encoded_object =json.JSONEncoder.default(self, obj)
        return encoded_object

def index(request):
    return render(request, 'index.html', {
        'request':       request,
        'organizations': Organization.objects.all(),
        'doctors':       Doctor.objects.all(),
        'patients':      Patient.objects.all(),
        'beds':          Bed.objects.all(),
    })

def user_login(request):
    username = password = ''
    if request.method == 'POST':        
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('land'))
            else:
                return HttpResponse('Account Inactive')
        else:
            return render(request, 'login.html', {
                'request': request,
                'status': 'Failed',
                'form': LoginForm(request.POST)
            })
    else:
        return render(request, 'login.html', {
            'request': request,
            'status': '',
            'form': LoginForm()
        })
    
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

def user_land(request):
    if(request.user.is_anonymous()):
        raise Http404()
    else:
        return HttpResponseRedirect(request.user.real().profile())

def doctors(request):
    return render(request, 'doctors.html', {
        'request': request,
        'doctors': Doctor.objects.all()
    })

def patients(request):
    return render(request, 'patients.html', {
        'request': request,
        'patients': Patient.objects.all()
    })

def patient(request, patient_id):
    patient = Patient.objects.get(id=patient_id)
    notices = []
    stories = []
    admissions = []
    appointments = []
    doctors = []
    
    if request.user.is_authenticated():
        if patient.admission() == None:
            admission = None
        else:
            try:
                admission = patient.admission().regularadmission
                story     = admission.story
                try:
                    doctor = story.scheduledvisit.doctor
                except ScheduledVisit.DoesNotExist:
                    try:
                        doctor = story.randomvisit.doctor
                    except RandomVisit.DoesNotExist:
                        doctor = None
                
            except RegularAdmission.DoesNotExist:
                admission = patient.admission()
                story     = None
                doctor    = None
                
            notices.append(Notice(Notice.Information, "Patient Currently Admitted",
                       "Patient Currently Admitted to %s on %s %s" %
                         (admission.org.get_full_name(),
                          admission.admitted,
                          doctor and ("by %s" % doctor.get_full_name()) or "[Emergency]")) )
            
        # if(request.user.is_patient() and request.user.id == patient.id):
        #     stories = patient.stories.all()
        #     admissions = patient.admissions.all()
        #     appointments = patient.appointments.all()
        # elif (request.user.is_doctor()):
        #     doctor = request.user.real()
        #     stories = patient.stories.filter(doctor=doctor)
        #     admissions = patient.admissions.all()
        #     appointments = patient.appointments.filter(doctor=doctor)
        
        stories         = StoryAccess().all(request.user, patient)
        admissions      = AdmissionAccess().all(request.user, patient)
        appointments    = AppointmentAccess().all(request.user, patient)

    return render(request, 'patient.html', {
        'request': request,
        'patient': patient,
        'stories': stories,
        'notices': notices,
        'admissions': admissions,
        'appointments': appointments
    })

def doctor(request, doctor_id):
    # pdb.set_trace()
    
    stories = []
    patients = []
    admissions = []
    appointments = []
    
    doctor = Doctor.objects.get(id=doctor_id)
    # if request.user.is_authenticated():    
    #     # if a doctor visits his/her own profile
    #     if(request.user.is_doctor() and request.user.id == doctor.id):
    #         stories = doctor.stories.all()
    #         patients = doctor.patients()
    #         admissions =  [a for a in [p.admission() for p in patients] if a is not None]
    #         appointments = doctor.appointments.all()
    #     else:
    #         # if a patient visits doctor's profile
    #         if request.user.is_patient():
    #             patient = request.user.real()
    #             stories = doctor.stories.filter(patient=patient)
    #             patients = [patient]
    #             admissions = [a for a in [p.admission() for p in patients] if (a is not None and a.doctor() == doctor)]
    #             appointments = doctor.appointments.filter(patient=patient)
    
    stories         = StoryAccess().all(request.user, doctor)
    admissions      = AdmissionAccess().all(request.user, doctor)
    appointments    = AppointmentAccess().all(request.user, doctor)
    patients        = list(set([story.patient for story in stories]))
        
    return render(request, 'doctor.html', {
        'request':      request,
        'doctor':       doctor,
        'stories':      stories,
        'patients':     patients,
        'admissions':   admissions,
        'appointments': appointments,
        'story_form':   RandomVisitCreationForm()
    })

def organizations(request):
    return render(request, 'organizations.html', {
        'request': request,
        'organizations': Organization.objects.all()
    })

def admission(request, admission_id):
    admission = Admission.objects.get(id=admission_id)
    return render(request, 'admission.html', {
        'request': request,
        'admission': admission,
        'form': TaskCreationForm(initial = {'admission': admission_id})
    })

def patient_admissions(request, patient_id):
    patient = Patient.objects.get(id=patient_id)
    notices = []
    
    if patient.admission() == None:
        admission = None
    else:
        try:
            admission = patient.admission().regularadmission
            story     = admission.story
            try:
                doctor = story.scheduledvisit.doctor
            except ScheduledVisit.DoesNotExist:
                try:
                    doctor = story.randomvisit.doctor
                except RandomVisit.DoesNotExist:
                    doctor = None
                
            
        except RegularAdmission.DoesNotExist:
            admission = patient.admission()
            story     = None
            doctor    = None
            
        notices.append(Notice(Notice.Information, "Patient Currently Admitted",
                   "Patient Currently Admitted to %s on %s %s" %
                     (admission.org.get_full_name(),
                      admission.admitted,
                      doctor and ("by %s" % doctor.get_full_name()) or "[Emergency]")) )
        
    admissions = AdmissionAccess().all(request.user, patient)
    
    return render(request, 'app/patient/admissions.html', {
        'request': request,
        'patient': patient,
        'notices': notices,
        'admissions': admissions
    })

def patient_appointments(request, patient_id):
    patient = Patient.objects.get(id=patient_id)
    notices = []
    
    if patient.admission() == None:
        admission = None
    else:
        try:
            admission = patient.admission().regularadmission
            story     = admission.story
            try:
                doctor = story.scheduledvisit.doctor
            except ScheduledVisit.DoesNotExist:
                try:
                    doctor = story.randomvisit.doctor
                except RandomVisit.DoesNotExist:
                    doctor = None
                
            
        except RegularAdmission.DoesNotExist:
            admission = patient.admission()
            story     = None
            doctor    = None
            
        notices.append(Notice(Notice.Information, "Patient Currently Admitted",
                   "Patient Currently Admitted to %s on %s %s" %
                     (admission.org.get_full_name(),
                      admission.admitted,
                      doctor and ("by %s" % doctor.get_full_name()) or "[Emergency]")) )
    
    appointments = AppointmentAccess().all(request.user, patient)
    
    return render(request, 'app/patient/appointments.html', {
        'request': request,
        'patient': patient,
        'notices': notices,
        'appointment_form': AppointmentCreationForm(),
        'appointments': appointments
    })

def patient_stories(request, patient_id):
    patient = Patient.objects.get(id=patient_id)
    notices = []
    stories = []
    
    if patient.admission() == None:
        admission = None
    else:
        try:
            admission = patient.admission().regularadmission
            story     = admission.story
            try:
                doctor = story.scheduledvisit.doctor
            except ScheduledVisit.DoesNotExist:
                try:
                    doctor = story.randomvisit.doctor
                except RandomVisit.DoesNotExist:
                    doctor = None
                
            
        except RegularAdmission.DoesNotExist:
            admission = patient.admission()
            story     = None
            doctor    = None
            
        notices.append(Notice(Notice.Information, "Patient Currently Admitted",
                   "Patient Currently Admitted to %s on %s %s" %
                     (admission.org.get_full_name(),
                      admission.admitted,
                      doctor and ("by %s" % doctor.get_full_name()) or "[Emergency]")) )
        
    stories = StoryAccess().all(request.user, patient)

    # pdb.set_trace()
    return render(request, 'app/patient/ministories.html', {
        'request': request,
        'patient': patient,
        'stories': stories,
        'notices': notices,
        'story_form': RandomVisitCreationForm()
    })

def patient_sensors(request, patient_id):
    patient = Patient.objects.get(id=patient_id)
    notices = []
    sensors = []
    
    if patient.admission() == None:
        admission = None
    else:
        try:
            admission = patient.admission().regularadmission
            story     = admission.story
            try:
                doctor = story.scheduledvisit.doctor
            except ScheduledVisit.DoesNotExist:
                try:
                    doctor = story.randomvisit.doctor
                except RandomVisit.DoesNotExist:
                    doctor = None
                
            
        except RegularAdmission.DoesNotExist:
            admission = patient.admission()
            story     = None
            doctor    = None
            
        notices.append(Notice(Notice.Information, "Patient Currently Admitted",
                   "Patient Currently Admitted to %s on %s %s" %
                     (admission.org.get_full_name(),
                      admission.admitted,
                      doctor and ("by %s" % doctor.get_full_name()) or "[Emergency]")) )
 
    # pdb.set_trace()
    return render(request, 'app/patient/sensors.html', {
        'request': request,
        'patient': patient,
        'notices': notices,
        'patient_id': patient.id
    })

def patient_doctors(request, patient_id):
    patient = Patient.objects.get(id=patient_id)
    notices = []
    
    if patient.admission() == None:
        admission = None
    else:
        try:
            admission = patient.admission().regularadmission
            story     = admission.story
            try:
                doctor = story.scheduledvisit.doctor
            except ScheduledVisit.DoesNotExist:
                try:
                    doctor = story.randomvisit.doctor
                except RandomVisit.DoesNotExist:
                    doctor = None
                
        except RegularAdmission.DoesNotExist:
            admission = patient.admission()
            story     = None
            doctor    = None
            
        notices.append(Notice(Notice.Information, "Patient Currently Admitted",
                   "Patient Currently Admitted to %s on %s %s" %
                     (admission.org.get_full_name(), admission.admitted,
                      doctor and ("by %s" % doctor.get_full_name()) or "[Emergency]")) )
        
    visits = patient.visits()

    return render(request, 'app/patient/doctors.html', {
        'request': request,
        'patient': patient,
        'visits': visits
    })

def patient_visits(request, patient_id, doctor_id):
    patient = Patient.objects.get(id=patient_id)
    doctor  = Doctor.objects.get(id=doctor_id)
    
    visits = StoryAccess().all(request.user, patient).filter(doctor=doctor)
    
    notices = []
    
    if patient.admission() == None:
        admission = None
    else:
        try:
            admission = patient.admission().regularadmission
            story     = admission.story
            try:
                doctor = story.scheduledvisit.doctor
            except ScheduledVisit.DoesNotExist:
                try:
                    doctor = story.randomvisit.doctor
                except RandomVisit.DoesNotExist:
                    doctor = None
                
            
        except RegularAdmission.DoesNotExist:
            admission = patient.admission()
            story     = None
            doctor    = None
            
        notices.append(Notice(Notice.Information, "Patient Currently Admitted",
                   "Patient Currently Admitted to %s on %s %s" %
                     (admission.org.get_full_name(),
                      admission.admitted,
                      doctor and ("by %s" % doctor.get_full_name()) or "[Emergency]")) )
    
    return render(request, 'app/patient/visits.html', {
        'request': request,
        'patient': patient,
        'doctor':  doctor,
        'notices': notices,
        'visits':  visits
    })

class appointment_creation(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            raise PermissionDenied()
        
        form = AppointmentCreationForm(request.POST)
        # form.org = Organization.objects.all()[0]
        if form.is_valid():
            patient = None
            try:
                patient = request.user.patient
            except Patient.DoesNotExist:
                patient = None
                
            appointment = form.save(commit=False)
            if patient:
                appointment.patient = patient
                appointment.save()
                return HttpResponse(json.dumps({
                    'success': True,
                    'errors':  []
                }), content_type='application/json; charset=UTF-8')
            else:
                raise PermissionDenied()
        else:
            return HttpResponse(json.dumps({
                'success' : False,
                'errors' : dict(form.errors.items())
            }), content_type='application/json; charset=UTF-8')
        
class random_story_creation(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            raise PermissionDenied()
        
        form = RandomVisitCreationForm(request.POST)
        if form.is_valid():
            doctor = None
            try:
                doctor = request.user.doctor
            except Patient.DoesNotExist:
                doctor = None
                
            story = form.save(commit=False)
            if doctor:
                story.doctor = doctor
                story.when = datetime.now()
                status = story.save()
                form.save_m2m()
                return HttpResponse(json.dumps({
                    'success': True,
                    'errors':  []
                }), content_type='application/json; charset=UTF-8')
            else:
                raise PermissionDenied()
        else:
            return HttpResponse(json.dumps({
                'success' : False,
                'errors' : dict(form.errors.items())
            }), content_type='application/json; charset=UTF-8')

class negotiation_creation(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            raise PermissionDenied()
        
        form = NegotiationForm(request.POST)
        
        if form.is_valid():
            negotiation = form.save(commit=False)
            if patient:
                negotiation.who = request.user
                negotiation.save()
                return HttpResponse(json.dumps({
                    'success': True,
                    'errors':  []
                }), content_type='application/json; charset=UTF-8')
            else:
                raise PermissionDenied()
        else:
            return HttpResponse(json.dumps({
                'success' : False,
                'errors' : dict(form.errors.items())
            }), content_type='application/json; charset=UTF-8')
        
class task_creation(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            raise PermissionDenied()
        user = request.user.real()
        if isinstance(user, Patient):
            raise PermissionDenied()
        
        admission_id = kwargs['admission_id']
        form = TaskCreationForm(request.POST)
        
        if form.is_valid():
            task = form.save(commit=False)
            task.who = request.user
            task.save()
            return HttpResponse(json.dumps({
                'success': True,
                'task': task.id,
                'errors':  []
            }), content_type='application/json; charset=UTF-8')
        else:
            return HttpResponse(json.dumps({
                'success' : False,
                'errors' : dict(form.errors.items())
            }), content_type='application/json; charset=UTF-8')

def organization_timeline(request, organization_id):
    try:
        organization = Organization.objects.get(id=organization_id)
        res = {}
        timeline = {}
        events = []
        res['timeline'] = timeline
        timeline['headline'] = organization.name + ' Events '
        timeline['type'] = 'default'
        timeline['text'] = ''
        timeline['date'] = events
        timeline['asset'] = {
            'media': '',
            'credit': '',
            'caption': ''
        }
        admissions = Admission.objects.filter(org=organization_id)
        for admission in admissions:
            event = {}
            try:
            	regular_admission = admission.regularadmission
            	story = regular_admission.story
            	event['headline'] = '<a href=\'/identity/admission/'+ str(admission.id) +'\'>'+story.subject+'</a>'
            	event['text'] = story.body
            except Exception, e:
            	event['headline'] = '<a href=\'/identity/admission/'+ str(admission.id) +'\'>'+'Emergency Admission'+'</a>'
            	event['text'] = 'Emergency Admission'

            
            event['startDate'] = admission.admitted
            if(admission.released):
                event['endDate'] = admission.released
           
            
            asset = {}
            asset['media'] = ''
            buff = '<div class=\'patient-tasks\'><ul class=\'patient-tasks-list\'>'
            for task in admission.tasks.order_by('-when')[:3]:
                buff += '<li class=\'patient-tasks-list-item\'>';
                buff += '<div class=\'task-dt\'>'
                buff +=     '<div class=\'task-date\'>'+ unicode(task.when.date()) +'</div>'
                buff +=     '<div class=\'task-time\'>'+ unicode(task.when.time()) +'</div>'
                buff += '</div>'
                buff += '<div class=\'task-icon task-icon-status-'+str(task.status())+'\'>'
                buff +=     '<input type=hidden name=\'task_id\' value=\''+ str(task.id) +'\' class=\'data\' />'
                buff += '</div>'
                buff += '<div class=\'task-main\'>'
                buff +=     '<div class=\'task-subject\'>'+ task.subject +'</div>'
                buff +=     '<div class=\'task-body\'>'+ task.body +'</div>'
                buff += '</div>'
                buff += '</li>'
                
            buff += '</ul></div>'
            
            asset['media'] = buff
            
            asset['credit'] = admission.patient.get_full_name()
            asset['caption'] = ''
            if admission.tasks.count() > 0:
                event['asset'] = asset;
                
            events.append(event)
        
    except Organization.DoesNotExist:
        raise Http404

    return HttpResponse(json.dumps(res, cls=DateTimeEncoder), content_type='application/json')

def organization(request, organization_id):
    try:
        organization = Organization.objects.get(id=organization_id)
    except Organization.DoesNotExist:
        raise Http404
    
    return render(request, 'organization.html', {
        'organization': organization
    })

def post_activity(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        raise Http404
    form = ActivityForm(request.POST or None)
    
    if request.method == 'GET':
        return render(request, 'post_activity.html', {
            'form': form,
            'form_action' : "/activity/create/"+task_id
        })
    elif request.method == 'POST':
        if form.is_valid():
            if request.user.is_authenticated():
                form = form.save(commit = False)
                form.when = datetime.now()
                form.who = request.user
                form.task = task
                form.save()
                return HttpResponse(json.dumps({
                    'task': task.id,
                    'activity': form.id,
                    'success': True
                }), content_type='application/json; charset=UTF-8')
            else:
                return HttpResponse(json.dumps({
                    'success': False,
                    'errors': {"_": ["user not logged in"]},
                }), content_type='application/json; charset=UTF-8')
        else:
            return HttpResponse(json.dumps({
                'success': False,
                'errors': dict(form.errors.items()),
            }), content_type='application/json; charset=UTF-8')
        
def _task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        full = request.GET.get('full', None)
        if(full == None):
            return TaskSprite(request, task)
        else:
            return render(request, 'sprite/_task.html', {
                'request': request,
                'task': task
            })
    except Task.DoesNotExist:
        raise Http404
    
def _story(request, story_id):
    try:
        story = Story.objects.get(id=story_id)
        return StoryViewerSprite(request, story)
    except Story.DoesNotExist:
        return Http404

def _prescription(request, story_id):
    try:
        story = Story.objects.get(id=story_id)
        prescriptions = []
        complaints    = []
        if story.is_prescription:
            story.body = json.loads(story.body)
            prescriptions.append(story)
            complaints = story.refers_to.all()
        else:
            complaints.append(story)
            for s in story.refered_by.all():
                s.body = json.loads(s.body)
                prescriptions.append(s)
        
        return PrescriptionViewerSprite(request, story, complaints, prescriptions)
    except Story.DoesNotExist:
        return Http404
    
def _activity(request, activity_id):
    try:
        activity = Activity.objects.get(id=activity_id)
        return ActivitySprite(request, activity)
    except Activity.DoesNotExist:
        raise Http404
    
def _activities(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        return render(request, 'sprite/_activities.html', {
            'request': request,
            'activities': task.activities.all()
        })
    except Task.DoesNotExist:
        raise Http404
    
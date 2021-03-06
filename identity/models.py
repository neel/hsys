from __future__ import unicode_literals
import re
import warnings
from django.db import models
from django.db.models.manager import EmptyManager
from django.db.models import Count
from django.utils import timezone
from datetime import date
from django.core import validators
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils.http import urlquote
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from django.contrib import auth
from django.contrib.auth.hashers import check_password, make_password, is_password_usable, UNUSABLE_PASSWORD_PREFIX
from django.contrib.auth.signals import user_logged_in
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import AbstractBaseUser, AbstractUser, UserManager, PermissionsMixin
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django.core.urlresolvers import reverse
from django.db import models
from datetime import datetime

class HmsUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid username.'), 'invalid')
        ])
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'auth_user'
        
    def get_full_name(self):
        return '%s|%s' % (self.username, self.email)        

    def get_short_name(self):
        return self.username

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.username)

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])
        
    def __unicode__(self):
        return self.get_full_name();

    def get_profile(self):
        """
        Returns site-specific profile for this user. Raises
        SiteProfileNotAvailable if this site does not allow profiles.
        """
        warnings.warn("The use of AUTH_PROFILE_MODULE to define user profiles has been deprecated.",
            PendingDeprecationWarning)
        if not hasattr(self, '_profile_cache'):
            from django.conf import settings
            if not getattr(settings, 'AUTH_PROFILE_MODULE', False):
                raise SiteProfileNotAvailable(
                    'You need to set AUTH_PROFILE_MODULE in your project '
                    'settings')
            try:
                app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
            except ValueError:
                raise SiteProfileNotAvailable(
                    'app_label and model_name should be separated by a dot in '
                    'the AUTH_PROFILE_MODULE setting')
            try:
                model = models.get_model(app_label, model_name)
                if model is None:
                    raise SiteProfileNotAvailable(
                        'Unable to load the profile model, check '
                        'AUTH_PROFILE_MODULE in your project settings')
                self._profile_cache = model._default_manager.using(
                                   self._state.db).get(user__id__exact=self.id)
                self._profile_cache.user = self
            except (ImportError, ImproperlyConfigured):
                raise SiteProfileNotAvailable
        return self._profile_cache
    
    def real(self, ):
        try: return self.doctor
        except Doctor.DoesNotExist:
            try: return self.operator
            except Operator.DoesNotExist:
                try: return self.patient
                except Patient.DoesNotExist:
                    try: return self.organization
                    except Organization.DoesNotExist:
                        return self
                    
    def is_doctor(self):
        return self.real().__class__ == Doctor
    
    def is_patient(self):
        return self.real().__class__ == Patient
    
    def is_operator(self):
        return self.real().__class__ == Operator
    
    def is_organization(self):
        return self.real().__class__ == Organization
                    
    def really(self, user_type):
        return isinstance(self.real(), user_type)
    

class Person(HmsUser):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name  = models.CharField(_('last name'), max_length=30, blank=True)
    dob        = models.DateField('Date Of Birth')
    sex        = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address    = models.CharField(max_length=300, blank=True)
    
    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name.strip()
    
    def age(self):
        delta = (date.today() - self.dob)
        return delta    

    class Meta:
        abstract = True
    

class Patient(Person):
    
    def get_full_name(self):
        return '%s. %s' % ( ('Mr', 'Ms')[self.sex == 'F'], super(Patient, self).get_full_name())

    def get_short_name(self):
        return '%s. %s' % (('Mr', 'Ms')[self.sex == 'F'], super(Patient, self).get_short_name())
    
    def admission(self):
        admissions = self.admissions.filter(released = None)
        return admissions.count() > 0 and admissions.latest('admitted') or None
    
    def doctors(self):
        id_list = self.stories.values_list('doctor', flat=True).distinct()
        return Doctor.objects.filter(pk__in=set(id_list))

    def visits(self):
        visits = dict()
        for story in self.stories.all():
            if(visits.has_key(story.doctor)):
                visits[story.doctor] = visits[story.doctor] + 1
            else:
                visits[story.doctor] = 1
        return visits

    def profile(self):
        return reverse('patient', args=(self.id, ))
    
    
class Organization(HmsUser):
    name    = models.CharField(_('Name'), max_length=30, blank=True)
    lat     = models.IntegerField()
    lng     = models.IntegerField()
    website = models.CharField(max_length=64)
    address = models.CharField(max_length=300, blank=True)
    doctors = models.ManyToManyField('Doctor', through='Membership', blank=True)
    
    def get_full_name(self):
        return self.name.strip()

    def get_short_name(self):
        return self.name
    
    def profile(self):
        return reverse('org', args=(self.id, ))
    
    class Meta:
        abstract = False
    

class Doctor(Person):
    paramedic     = models.BooleanField()
    organizations = models.ManyToManyField(Organization, through='Membership', blank=True)
    
    def get_full_name(self):
        return '%s. %s' % ('Dr', super(Doctor, self).get_full_name())

    def get_short_name(self):
        return '%s. %s' % ('Dr', super(Doctor, self).get_short_name())
    
    def stories(self):
        stories = []
        random_visits = self.random_visits.all()
        scheduled_visits = []
        for appointment in self.appointments.all():
            try:
                visits = appointment.scheduled_visit.all()
                for visit in visits:
                    scheduled_visits.append(visit)
            except ScheduledVisit.DoesNotExist:
                pass
            
        scheduled_visits.extend(random_visits)
        stories = scheduled_visits
        
        return stories;
      
    def patients(self):
        id_list = self.stories.values_list('patient', flat=True).distinct()
        return Patient.objects.filter(pk__in=set(id_list))
    
    def profile(self):
        return reverse('doctor', args=(self.id, ))
    
    
class Operator(Person):
    org = models.ForeignKey(Organization, related_name="operators")
    
    def __unicode__(self):
        return '%s from %s' % (self.get_full_name(), self.org.get_full_name())
    
    def profile(self):
        return reverse('operator', args=(self.id, ))
    
class Membership(models.Model):
    doctor = models.ForeignKey(Doctor)
    org = models.ForeignKey(Organization)
    
    class Meta:
        unique_together = ('doctor', 'org')
    
    def __unicode__(self):
        return self.doctor.__unicode__()+' <> '+self.org.__unicode__()
 
   
class Story(models.Model):
    when    = models.DateTimeField('when')
    patient = models.ForeignKey(Patient, related_name="stories")
    doctor  = models.ForeignKey(Doctor, related_name="stories")
    subject = models.CharField(max_length=1500)
    body    = models.TextField()
    refers_to = models.ManyToManyField('Story', related_name="refered_by", blank=True)

    def __unicode__(self):
        return "%s" % (self.subject)
    
class ScheduledVisit(Story):
    appointment = models.ForeignKey('Appointment', related_name="scheduled_visit")

    def __unicode__(self):
        return "%s as appointed %s" % (super(ScheduledVisit, self).__unicode__(), self.appointment);
    
class AdmissionVisit(Story):
    admission = models.ForeignKey('Admission', related_name="admission_visit")
    
    def __unicode__(self):
        return "%s as admitted %s" % (super(ScheduledVisit, self).__unicode__(), self.admission);

class RandomVisit(Story):
    
    def __unicode__(self):
        return "%s at %s with %s and %s" % (super(RandomVisit, self).__unicode__(), self.when, self.patient, self.doctor);
    
    
class Bed(models.Model):
   local_id     = models.CharField(max_length=16)
   org = models.ForeignKey(Organization, related_name="beds")
   
   def __unicode__(self):
       return self.local_id+'@'+self.org.__unicode__()
    

class Admission(models.Model):
    patient   = models.ForeignKey(Patient, related_name="admissions")
    admitted  = models.DateTimeField('Admittied On')
    released  = models.DateTimeField(null=True, blank=True)
    org       = models.ForeignKey(Organization, related_name="admissions")
    
    def doctor(self):
        try:
            return self.regularadmission.story.doctor
        except RegularAdmission.DoesNotExist:
            return None
        
    def real(self):
        try: return self.regularadmission
        except RegularAdmission.DoesNotExist:
            try: return self.EmergencyAdmission
            except EmergencyAdmission.DoesNotExist:
                return self
            
    def is_regular(self):
        return self.real().__class__ == RegularAdmission
    
    def is_emergency(self):
        return self.real().__class__ == EmergencyAdmission
    
    def __unicode__(self):
        return self.patient.__unicode__()+' -> '+self.org.__unicode__()
    
       
class RegularAdmission(Admission):
    story = models.ForeignKey(Story, related_name="admissions")
    
    def doctor(self):
		return self.story.doctor
		
    def doctor_id(self):
		return self.doctor().id
    
class EmergencyAdmission(Admission):
    pass
    
class Task(models.Model):
    admission = models.ForeignKey(Admission, related_name="tasks")
    when      = models.DateTimeField('When')
    subject   = models.CharField(max_length=1500)
    body      = models.TextField()
    who       = models.ForeignKey(HmsUser, related_name="tasks")
    
    def status(self):
        try:
            return self.activities.latest("when").status
        except Activity.DoesNotExist:
            return list(Activity.ACTIVITY_CHOICES)[0]
    
    def lsup(self):
        if(self.activities.count() == 0):
            return None
        return self.activities.latest("when").when
        
    
class Appointment(models.Model):
    patient = models.ForeignKey(Patient, related_name="appointments")
    doctor  = models.ForeignKey(Doctor, related_name="appointments")
    schedule= models.DateTimeField('When')
    created = CreationDateTimeField('Created At')
    note    = models.TextField(null=True, blank=True)
    org = models.ForeignKey(Organization, related_name='appointments', null=True)
    
    def status(self):
        try:
            return self.negotiations.order_by("-created")[0].status
        except Negotiation.DoesNotExist:
            return list(Negotiation.NEGOTIATION_STATUS)[2]
        except IndexError:
            return list(Negotiation.NEGOTIATION_STATUS)[2]
        
    def status_key(self):
        return self.status()[0]
        
    def get_status_display(self):
        try:
            return self.negotiations.order_by("-created")[0].get_status_display()
        except Negotiation.DoesNotExist:
            return 'Waiting for Approval'
        except IndexError:
            return 'Waiting for Approval'
        
    def when(self):
        try:
            return self.negotiations.order_by("-created")[0].when
        except Negotiation.DoesNotExist:
            return None
        except IndexError:
            return None
        
    def __unicode__(self):
        return "Appointment for %s with %s" % (self.doctor, self.patient)
    
class Negotiation(models.Model):
    NEGOTIATION_STATUS = (
        ('F', 'Fixed'),
        ('C', 'Canceled'),
        ('W', 'Waiting for Approval')
    )
    appointment = models.ForeignKey(Appointment, related_name="negotiations")
    status      = models.CharField(max_length=1, choices=NEGOTIATION_STATUS, default='W')
    who         = models.ForeignKey(HmsUser, related_name="negotiations")
    created     = CreationDateTimeField('Created At')
    note        = models.TextField(null=True, blank=True)
    when        = models.DateTimeField('When', null=True, blank=True)
    
    def creation_delay(self):
        return self.created - self.appointment.created
       
    def __unicode__(self):
        return "Alocation on %s [%s] for %s" %(self.when, self.status, self.appointment)
    
class Activity(models.Model):
    ACTIVITY_CHOICES = (
        ('O', 'Open'),
        ('R', 'Reopen'),
        ('D', 'Done'),
        ('H', 'Hold'),
        ('C', 'Cancel'),
    )
    task     = models.ForeignKey(Task, related_name="activities")
    who      = models.ForeignKey(HmsUser, related_name="activities")
    when     = models.DateTimeField('when')
    note     = models.TextField()
    status   = models.CharField(max_length=1, choices=ACTIVITY_CHOICES)
    
    def delay(self):
        return self.when - self.task.when
    
    def actor(self):
        try: return self.who.doctor
        except Doctor.DoesNotExist:
            try: return self.who.operator
            except Operator.DoesNotExist:
                try: return self.who.patient
                except Patient.DoesNotExist:
                    try: return self.who.organization
                    except Organization.DoesNotExist:
                        return self.who
    
    class Meta:
        ordering = ['-when']
        
    
    


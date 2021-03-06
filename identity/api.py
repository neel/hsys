from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from identity.models import HmsUser, Patient, Story, Doctor, Organization, Admission, Activity, Bed, Task, RandomVisit, Appointment, RegularAdmission, EmergencyAdmission
from tastypie import fields
from django.db.models import Q
from tastypie.paginator import Paginator
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication, BasicAuthentication
from django.conf.urls import url, include
from django.contrib.auth import authenticate, login, logout
from tastypie.utils import trailing_slash
from django.http import HttpResponse
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpNotFound
 
class UserResource(ModelResource):
    class Meta:
        queryset = HmsUser.objects.all()
        fields = ['first_name', 'last_name', 'email']
        allowed_methods = ['get', 'post']
        resource_name = 'user'

    # renamed override_urls as it is deprecated
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/login%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('login'), name="api_login"),
            url(r'^(?P<resource_name>%s)/logout%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('logout'), name='api_logout'),
        ]

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))

        username = data.get('username', '')
        password = data.get('password', '')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return self.create_response(request, {
                    'success': True,
                    'user': user.id
                })
            else:
                return self.create_response(request, {
                    'success': False,
                    'reason': 'disabled',
                    }, HttpForbidden )
        else:
            return self.create_response(request, {
                'success': False,
                'reason': 'incorrect',
                }, HttpUnauthorized )

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, { 'success': True })
        else:
            return self.create_response(request, { 'success': False }, HttpUnauthorized)
 
class NoMetaPaginator(Paginator):
    def page(self):
        res = super(NoMetaPaginator, self).page()
        del res['meta']
        return res

class StoryResource(ModelResource):
    when = fields.DateTimeField(attribute='when', readonly=True, null=True, blank=True)
    doctor = fields.ToOneField('identity.api.DoctorShallowResource', 'doctor', full=True)
    patient = fields.ToOneField('identity.api.PatientShallowResource', 'patient', full=True)   
    
    class Meta:
        queryset = Story.objects.all()
        filtering = {
            'doctor': ALL_WITH_RELATIONS,
            'patient': ALL_WITH_RELATIONS,
            'when':  ['range', 'gt', 'gte', 'lt', 'lte'],
            'subject': ['like']
        }
        
  
class RandomVisitResource(ModelResource):
    doctor = fields.ToOneField('identity.api.DoctorResource', 'doctor')
    patient = fields.ToOneField('identity.api.PatientResource', 'patient')  
    story = fields.ToOneField('identity.api.StoryResource', 'story_ptr', readonly=True) 

    class Meta:
        queryset = RandomVisit.objects.all()
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True

class OrganizationResource(ModelResource):
    doctors = fields.ToManyField('identity.api.DoctorResource', 'doctors', null=True)
    beds    = fields.ToManyField('identity.api.BedResource', 'beds', null=True)
    user    = fields.ToOneField('identity.api.UserResource', 'hmsuser_ptr', readonly=True)
    
    class Meta:
        queryset = Organization.objects.all()
        excludes = ['login', 'password']


class DoctorResource(ModelResource):
    organizations = fields.ToManyField('identity.api.OrganizationResource', 'organizations', null=True)
    #visits        = fields.DictField(attribute='visits', readonly=True)
    
    class Meta:
        queryset = Doctor.objects.all()
        excludes = ['login', 'password', 'is_active', 'is_staff', 'is_superuser', 'last_login']
        filtering = {
            'id': ALL_WITH_RELATIONS
        }
    
class DoctorShallowResource(ModelResource):
    class Meta:
        queryset = Doctor.objects.all()
        excludes = ['login', 'password', 'is_active', 'is_staff', 'is_superuser', 'last_login']
        filtering = {
            'id': ALL_WITH_RELATIONS
        }
    
# http://stackoverflow.com/questions/10021749/django-tastypie-advanced-filtering-how-to-do-complex-lookups-with-q-objects
# http://django-tastypie.readthedocs.org/en/latest/search.html?q=filter&check_keywords=yes&area=default
# http://ramblersamble.blogspot.in/2013/01/tastypie-using-custom-filters-without.html
# https://docs.djangoproject.com/en/1.5/topics/db/queries/#django.db.models.Q
# http://michalcodes4life.wordpress.com/2013/11/26/custom-tastypie-resource-from-multiple-django-models/    
class DoctorCatalogResource(ModelResource):
    organizations = fields.ToManyField('identity.api.OrganizationResource', 'organizations', null=True)
    #visits        = fields.DictField(attribute='visits', readonly=True)
    
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(DoctorCatalogResource, self).build_filters(filters)
        
        if('query' in filters):
            query = filters['query']
            query_parts = query.split(' ')
            
            qset = Q(first_name__istartswith=query_parts[0])
            for query_part in query_parts:
                qset |= (Q(first_name__icontains=query_part) | Q(last_name__icontains=query_part))
    
            orm_filters.update({'custom': qset})
            
        return orm_filters
    
    def apply_filters(self, request, applicable_filters):
        if 'custom' in applicable_filters:
            custom = applicable_filters.pop('custom')
        else:
            custom = None
            
        semi_filtered = super(DoctorCatalogResource, self).apply_filters(request, applicable_filters)
        return semi_filtered.filter(custom) if custom else semi_filtered
    
    class Meta:
        queryset = Doctor.objects.all()
        excludes = ['username', 'password', 'address', 'date_joined', 'is_active', 'is_staff', 'is_superuser', 'last_login']
        paginator_class = NoMetaPaginator
       
  
class PatientShallowResource(ModelResource):
    class Meta:
        queryset = Patient.objects.all()
        excludes = ['login', 'password', 'is_active', 'is_staff', 'is_superuser', 'last_login']
        authorization= Authorization()
        filtering = {
            'id': ALL_WITH_RELATIONS
        }
       
class PatientResource(ModelResource):
    appointments = fields.ToManyField('identity.api.AppointmentResource', 'appointments', full=True, use_in='detail', readonly=True)
    visits = fields.ToManyField('identity.api.StoryResource', 'stories', full=True, use_in='detail', readonly=True)
    admissions = fields.ToManyField('identity.api.AdmissionResource', 'admissions', null=True, use_in='detail', readonly=True)
    
    class Meta:
        queryset = Patient.objects.all()
        excludes = ['login', 'password', 'is_active', 'is_staff', 'is_superuser', 'last_login']
        authorization= Authorization()
        filtering = {
            'id': ALL_WITH_RELATIONS
        }
        
        
        
class PatientCatalogResource(ModelResource):
    #organizations = fields.ToManyField('identity.api.OrganizationResource', 'organizations', null=True)
    #visits        = fields.DictField(attribute='visits', readonly=True)
    
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(PatientCatalogResource, self).build_filters(filters)
        
        if('query' in filters):
            query = filters['query']
            query_parts = query.split(' ')
            
            qset = Q(first_name__istartswith=query_parts[0])
            for query_part in query_parts:
                qset |= (Q(first_name__icontains=query_part) | Q(last_name__icontains=query_part))
    
            orm_filters.update({'custom': qset})
            
        return orm_filters
    
    def apply_filters(self, request, applicable_filters):
        if 'custom' in applicable_filters:
            custom = applicable_filters.pop('custom')
        else:
            custom = None
            
        semi_filtered = super(PatientCatalogResource, self).apply_filters(request, applicable_filters)
        return semi_filtered.filter(custom) if custom else semi_filtered
    
    class Meta:
        queryset = Patient.objects.all()
        excludes = ['username', 'password', 'date_joined', 'is_active', 'is_staff', 'is_superuser', 'last_login']
        paginator_class = NoMetaPaginator
        
class BedResource(ModelResource):
 #   admissions = fields.ToManyField('identity.api.AdmissionResource', 'admissions', null=True)
    
    class Meta:
        queryset = Bed.objects.all()
        excludes = ['id']

class AdmissionResource(ModelResource):
    tasks = fields.ToManyField('identity.api.TaskResource', 'tasks', null=True, full=True)
    organization = fields.ToOneField('identity.api.OrganizationResource', 'org', full=True)
    patient = fields.ToOneField('identity.api.PatientShallowResource', 'patient', full=True)
    
    class Meta:
        queryset = Admission.objects.all()
        filtering = {
            'bed': ['exact'],
            'story': ['exact'],
            'patient': ['exact'],
            'admission': ['range', 'gt', 'gte', 'lt', 'lte'],
            'release': ['range', 'gt', 'gte', 'lt', 'lte']
        }
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        
class RegularAdmissionResource(ModelResource):
    tasks = fields.ToManyField('identity.api.TaskResource', 'tasks', null=True, full=True)
    patient = fields.ToOneField('identity.api.PatientShallowResource', 'patient', full=True)
    story = fields.ToOneField('identity.api.StoryResource', 'story', full=True)
    organization = fields.ToOneField('identity.api.OrganizationResource', 'org', full=True)
    doctor_id = fields.CharField(attribute='doctor_id', readonly=True)

    class Meta:
        queryset = RegularAdmission.objects.all()
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        
class EmergencyAdmissionResource(ModelResource):
    tasks = fields.ToManyField('identity.api.TaskResource', 'tasks', null=True, full=True)
    patient = fields.ToOneField('identity.api.PatientShallowResource', 'patient')
    organization = fields.ToOneField('identity.api.OrganizationResource', 'org', full=True)

    class Meta:
        queryset = EmergencyAdmission.objects.all()
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        
class TaskResource(ModelResource):
    activities = fields.ToManyField('identity.api.ActivityResource', 'activities', null=True, full=True)
    admission = fields.ToOneField('identity.api.AdmissionResource', 'admission')
    who = fields.ToOneField('identity.api.UserResource', 'who')
    lsup = fields.DateTimeField(attribute='lsup', readonly=True)
    
    class Meta:
        queryset = Task.objects.all()
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
    

class ActivityResource(ModelResource):
    who = fields.ToOneField('identity.api.UserResource', 'who')
    task = fields.ToOneField('identity.api.TaskResource', 'task')
    
    class Meta:
        queryset = Activity.objects.all()
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        excludes = ['id']

class AppointmentResource(ModelResource):
	doctor = fields.ToOneField('identity.api.DoctorShallowResource', 'doctor', full=True)
	patient = fields.ToOneField('identity.api.PatientShallowResource', 'patient', full=True)
	when = fields.DateTimeField(attribute='when', readonly=True)
	status = fields.CharField(attribute='status', readonly=True)

	class Meta:
		queryset = Appointment.objects.all()
		excludes = ['id']
		authorization = Authorization()

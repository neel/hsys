"""hsysi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from tastypie.api import Api
from identity.api import *
from identity import views
from django.contrib.auth import views as auth_views
from registration.backends.simple.views import RegistrationView
from identity.forms import PatientRegistrationForm, DoctorRegistrationForm, OperatorRegistrationForm

v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(PatientResource())
v1_api.register(DoctorResource())
v1_api.register(PatientShallowResource())
v1_api.register(DoctorShallowResource())
v1_api.register(DoctorCatalogResource())
v1_api.register(PatientCatalogResource())
v1_api.register(StoryResource())
v1_api.register(RandomVisitResource())
v1_api.register(OrganizationResource())
v1_api.register(BedResource())
v1_api.register(AdmissionResource())
v1_api.register(RegularAdmissionResource())
v1_api.register(EmergencyAdmissionResource())
v1_api.register(TaskResource())
v1_api.register(ActivityResource())
v1_api.register(AppointmentResource())

urlpatterns = [
    url(r'^accounts/register/patient/$', RegistrationView.as_view(form_class=PatientRegistrationForm), name='register_patient'),
    url(r'^accounts/register/doctor/$', RegistrationView.as_view(form_class=DoctorRegistrationForm), name='register_doctor'),
    url(r'^accounts/register/operator/$', RegistrationView.as_view(form_class=OperatorRegistrationForm), name='register_operator'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^user/land/$', views.user_land, name='land'),
    url(r'^user/login/$', views.user_login, name='login'),
    url(r'^user/logout/$',  auth_views.logout, {'next_page': '/user/login'}, name='logout'),
    url(r'^doctors/$', views.doctors, name='doctors'),
    url(r'^doctor/(?P<doctor_id>\d+)/$', views.doctor, name='doctor'),
    url(r'^patients/$', views.patients, name='patients'),
    url(r'^patient/(?P<patient_id>\d+)/$', views.patient, name='patient'),
    url(r'^patient/(?P<patient_id>\d+)/admissions$', views.patient_admissions, name='patient_admissions'),
    url(r'^patient/(?P<patient_id>\d+)/appointments$', views.patient_appointments, name='patient_appointments'),
    url(r'^patient/(?P<patient_id>\d+)/stories$', views.patient_stories, name='patient_stories'),
    url(r'^patient/(?P<patient_id>\d+)/doctors$', views.patient_doctors, name='patient_doctors'),
    url(r'^patient/(?P<patient_id>\d+)/sensors$', views.patient_sensors, name='patient_sensors'),
    url(r'^patient/(?P<patient_id>\d+)/visits/(?P<doctor_id>\d+)$', views.patient_visits, name='patient_visits'),
    url(r'^organizations/$', views.organizations, name='organizations'),
	url(r'organization/(?P<organization_id>\d+)/timeline.json', views.organization_timeline, name='organization_timeline'),
    url(r'organization/(?P<organization_id>\d+)/$', views.organization, name='organization'),
    url(r'^admission/(?P<admission_id>\d+)/$', views.admission, name='admission'),
    url(r'^task/create/(?P<admission_id>\d+)$', views.task_creation.as_view(), name='task_create'),
    url(r'^appointment/create/$', views.appointment_creation.as_view(), name='appointment_create'),
    url(r'^story/random/create/$', views.random_story_creation.as_view(), name='random_story_create'),
    url(r'^negotiation/create/$', views.negotiation_creation.as_view(), name='negotiation_create'),
    url(r'^activity/create/(?P<task_id>\d+)/$', views.post_activity, name="post_task_activity"),
    url(r'^_task/(?P<task_id>\d+)/$', views._task, name='_task'),
    url(r'^_activities/(?P<task_id>\d+)/$', views._activities, name='_activities'),
    url(r'^_activity/(?P<activity_id>\d+)/$', views._activity, name='_activity'),
    url(r'^_story/(?P<story_id>\d+)/$', views._story, name='_story'),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(v1_api.urls))
]

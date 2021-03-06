# A story, appointment, admission relates doctor and patient
# However an admission primarily belongs to a patient and and organization
# a doctor may be related indirectly via a story

from identity.models import *
from django.db.models import Q

class StoryAccess:
    # return what stories of owner that are accessible by user
    def all(self, user, owner, id=0):
        viewer = user
        if not viewer.is_authenticated():
            return []
        if(viewer.id == owner.id):
            return owner.stories.filter(id__gt=id).order_by('-when')
        elif(viewer.is_doctor() and owner.is_patient()):
            doctor  = viewer.real()
            patient = owner.real()
            return patient.stories.filter(id__gt=id, doctor=doctor).order_by('-when')
        elif(viewer.is_patient() and owner.is_doctor()):
            patient = viewer.real()
            doctor  = owner.real()
            return doctor.stories.filter(id__gt=id, patient=patient).order_by('-when')
        elif(viewer.is_doctor() and owner.is_doctor()):
            return []
        elif(viewer.is_patient() and owner.is_patient()):
            return []
        else:
            return []
        
class AppointmentAccess:
    # return what appointments of owner that are accessible by user
    def all(self, user, owner, id=0):
        viewer = user
        if not viewer.is_authenticated():
            return []
        if(viewer.id == owner.id):
            return owner.appointments.filter(id__gt=id).order_by('-schedule')
        elif(viewer.is_doctor() and owner.is_patient()):
            doctor  = viewer.real()
            patient = owner.real()
            return patient.appointments.filter(id__gt=id, doctor=doctor).order_by('-schedule')
        elif(viewer.is_patient() and owner.is_doctor()):
            patient = viewer.real()
            doctor  = owner.real()
            return doctor.appointments.filter(id__gt=id, patient=patient).order_by('-schedule')
        elif(viewer.is_organization() and owner.is_doctor()):
            organization = viewer.real()
            doctor  = owner.real()
            return organization.appointments.filter(id__gt=id, doctor=doctor).order_by('-schedule')
        elif(viewer.is_organization() and owner.is_patient()):
            organization = viewer.real()
            patient  = owner.real()
            return organization.appointments.filter(id__gt=id, patient=patient).order_by('-schedule')
        elif(viewer.is_doctor() and owner.is_doctor()):
            return []
        elif(viewer.is_patient() and owner.is_patient()):
            return []
        else:
            return []
        
class AdmissionAccess:
    # return what admissions of owner that are accessible by user
    def all(self, user, owner, id=0):
        viewer = user
        if not viewer.is_authenticated():
            return []
        if(viewer.id == owner.id and owner.is_patient()):
            return owner.admissions.filter(id__gt=id).order_by('-admitted')
        if(viewer.id == owner.id and owner.is_doctor()):
            doctor  = owner.real()
            organizations = owner.organizations.all()
            admissions = Admission.objects.filter(id__gt=id).filter(Q(org__in=organizations) | Q(regularadmission__story__doctor=doctor)).order_by('-admitted')
            #admissions.extend([a for a in Admission.objects.filter(id__gt=id).order_by('-admitted') if a.doctor() == doctor])
            return admissions
        elif(viewer.is_doctor() and owner.is_patient()):
            doctor  = viewer.real()
            patient = owner.real()
            return Admission.objects.filter(id__gt=id, patient=patient , regularadmission__story__doctor=doctor).order_by('-admitted')
        elif(viewer.is_patient() and owner.is_doctor()):
            patient = viewer.real()
            doctor  = owner.real()
            return Admission.objects.filter(id__gt=id, patient=patient , regularadmission__story__doctor=doctor).order_by('-admitted')
        elif(viewer.is_organization() and owner.is_doctor()):
            organization = viewer.real()
            doctor  = owner.real()
            return [admission for admission in [a for a in Admission.objects.filter(id__gt=id).order_by('-admitted') if a.org == organization] if admission.doctor() == doctor]
        elif(viewer.is_organization() and owner.is_patient()):
            organization = viewer.real()
            patient  = owner.real()
            return patient.admissions.filter(id__gt=id, org=organization).order_by('-admitted')
        elif(viewer.is_doctor() and owner.is_doctor()):
            return []
        elif(viewer.is_patient() and owner.is_patient()):
            return []
        else:
            return []
        

        
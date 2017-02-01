from django.contrib import admin
from django.conf.urls import include, url
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField, AdminPasswordChangeForm
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.db import transaction
from identity.models import *

class DoctorCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation',widget=forms.PasswordInput)
    
    class Meta:
        model = Doctor
        fields = ('email', 'first_name', 'last_name', 'dob', 'sex', 'address', 'paramedic')
    
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            msg = "Passwords don't match"
            raise forms.ValidationError(msg)
        return password2
    
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(DoctorCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    
class DoctorChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Doctor
        fields = '__all__'

    def clean_password(self):
        # Regardless of what the user provides, return the
        # initial value. This is done here, rather than on
        # the field, because the field does not have access
        # to the initial value
        return self.initial["password"]
    
class DoctorAdmin(UserAdmin):
    add_form = DoctorCreationForm
    form     = DoctorChangeForm
    
    fieldsets = (
        (None,              {'fields': ('username', 'email', 'password',)}),
        ('Personal info',   {'fields': ('first_name', 'last_name', 'dob', 'sex', 'address',)}),
        ('Medical info',    {'fields': ('paramedic',)}),
        ('Permissions',     {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    
    add_fieldsets = (
        (None,              {'fields': ('username', 'email', 'password1', 'password2',)}),
        ('Personal info',   {'fields': ('first_name', 'last_name', 'dob', 'sex', 'address',)}),
        ('Medical info',    {'fields': ('paramedic',)}),
        ('Permissions',     {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    
class PatientCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation',widget=forms.PasswordInput)
    
    class Meta:
        model = Patient
        fields = ('email', 'first_name', 'last_name', 'dob', 'sex', 'address',)
    
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            msg = "Passwords don't match"
            raise forms.ValidationError(msg)
        return password2
    
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(PatientCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    
class PatientChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Patient
        fields = '__all__'

    def clean_password(self):
        # Regardless of what the user provides, return the
        # initial value. This is done here, rather than on
        # the field, because the field does not have access
        # to the initial value
        return self.initial["password"]
    
class PatientAdmin(UserAdmin):
    add_form = PatientCreationForm
    form     = PatientChangeForm
    
    fieldsets = (
        (None,              {'fields': ('username', 'email', 'password',)}),
        ('Personal info',   {'fields': ('first_name', 'last_name', 'dob', 'sex', 'address',)}),
        ('Permissions',     {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    
    add_fieldsets = (
        (None,              {'fields': ('username', 'email', 'password1', 'password2',)}),
        ('Personal info',   {'fields': ('first_name', 'last_name', 'dob', 'sex', 'address',)}),
        ('Permissions',     {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

class OrganizationCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password Confirmation',widget=forms.PasswordInput)
    
    class Meta:
        model = Organization
        fields = ('email', 'name', 'address','website', 'lat', 'lng',)
    
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            msg = "Passwords don't match"
            raise forms.ValidationError(msg)
        return password2
    
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(OrganizationCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    
class OrganizationChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Organization
        fields = '__all__'

    def clean_password(self):
        # Regardless of what the user provides, return the
        # initial value. This is done here, rather than on
        # the field, because the field does not have access
        # to the initial value
        return self.initial["password"]
    
class OrganizationAdmin(admin.ModelAdmin):
    add_form_template = 'admin/auth/user/add_form.html'
    change_user_password_template = None
    
    add_form = OrganizationCreationForm
    form     = OrganizationChangeForm
    
    fieldsets = (
        (None,               {'fields': ('username', 'email', 'password',)}),
        ('Organization info',{'fields': ('name', 'address', 'website',)}),
        ('Location info',    {'fields': ('lat', 'lng',)}),
        ('Permissions',      {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates',  {'fields': ('last_login',)}),
    )
    
    add_fieldsets = (
        (None,               {'fields': ('username', 'email', 'password1', 'password2',)}),
        ('Organization info',{'fields': ('name', 'address', 'website',)}),
        ('Location info',    {'fields': ('lat', 'lng',)}),
        ('Permissions',      {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates',  {'fields': ('last_login',)}),
    )
    
    change_password_form = AdminPasswordChangeForm
    list_display = ('username', 'email', 'name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(OrganizationAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults.update({
                'form': self.add_form,
                'fields': admin.utils.flatten_fieldsets(self.add_fieldsets),
            })
        defaults.update(kwargs)
        return super(OrganizationAdmin, self).get_form(request, obj, **defaults)

    def get_urls(self):
        return [url(r'^(\d+)/password/$', self.admin_site.admin_view(self.user_change_password))]+super(OrganizationAdmin, self).get_urls()

    def lookup_allowed(self, lookup, value):
        # See #20078: we don't want to allow any lookups involving passwords.
        if lookup.startswith('password'):
            return False
        return super(OrganizationAdmin, self).lookup_allowed(lookup, value)

    # @sensitive_post_parameters_m
    # @csrf_protect_m
    # @transaction.commit_on_success
    def add_view(self, request, form_url='', extra_context=None):
        # It's an error for a user to have add permission but NOT change
        # permission for users. If we allowed such users to add users, they
        # could create superusers, which would mean they would essentially have
        # the permission to change users. To avoid the problem entirely, we
        # disallow users from adding users if they don't have change
        # permission.
        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                # Raise Http404 in debug mode so that the user gets a helpful
                # error message.
                raise Http404(
                    'Your user does not have the "Change user" permission. In '
                    'order to add users, Django requires that your user '
                    'account have both the "Add user" and "Change user" '
                    'permissions set.')
            raise PermissionDenied
        if extra_context is None:
            extra_context = {}
        username_field = self.model._meta.get_field(self.model.USERNAME_FIELD)
        defaults = {
            'auto_populated_fields': (),
            'username_help_text': username_field.help_text,
        }
        extra_context.update(defaults)
        return super(OrganizationAdmin, self).add_view(request, form_url,
                                               extra_context)

    # @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = get_object_or_404(self.queryset(request), pk=id)
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                msg = ugettext('Password changed successfully.')
                messages.success(request, msg)
                return HttpResponseRedirect('..')
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Change password: %s') % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': '_popup' in request.REQUEST,
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
        }
        return TemplateResponse(request,
            self.change_user_password_template or
            'admin/auth/user/change_password.html',
            context, current_app=self.admin_site.name)

    def response_add(self, request, obj, post_url_continue=None):
        """
        Determines the HttpResponse for the add_view stage. It mostly defers to
        its superclass implementation but is customized because the User model
        has a slightly different workflow.
        """
        # We should allow further modification of the user just added i.e. the
        # 'Save' button should behave like the 'Save and continue editing'
        # button except in two scenarios:
        # * The user has pressed the 'Save and add another' button
        # * We are adding a user in a popup
        if '_addanother' not in request.POST and '_popup' not in request.POST:
            request.POST['_continue'] = 1
        return super(OrganizationAdmin, self).response_add(request, obj,
                                                   post_url_continue)

class OperatorCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation',widget=forms.PasswordInput)
    
    class Meta:
        model = Operator
        fields = ('email', 'first_name', 'last_name', 'dob', 'sex', 'address', 'org')
    
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            msg = "Passwords don't match"
            raise forms.ValidationError(msg)
        return password2
    
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(OperatorCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    
class OperatorChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Operator
        fields = '__all__'

    def clean_password(self):
        # Regardless of what the user provides, return the
        # initial value. This is done here, rather than on
        # the field, because the field does not have access
        # to the initial value
        return self.initial["password"]
    
class OperatorAdmin(UserAdmin):
    add_form = OperatorCreationForm
    form     = OperatorChangeForm
    
    fieldsets = (
        (None,              {'fields': ('username', 'email', 'password',)}),
        ('Personal info',   {'fields': ('first_name', 'last_name', 'dob', 'sex', 'address',)}),
        ('Medical info',    {'fields': ('org',)}),
        ('Permissions',     {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    
    add_fieldsets = (
        (None,              {'fields': ('username', 'email', 'password1', 'password2',)}),
        ('Personal info',   {'fields': ('first_name', 'last_name', 'dob', 'sex', 'address',)}),
        ('Medical info',    {'fields': ('org',)}),
        ('Permissions',     {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    

admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Operator, OperatorAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Membership)
admin.site.register(Story)
admin.site.register(ScheduledVisit)
admin.site.register(RandomVisit)
admin.site.register(Bed)
admin.site.register(Admission)
admin.site.register(RegularAdmission)
admin.site.register(EmergencyAdmission)
admin.site.register(Task)
admin.site.register(Activity)
admin.site.register(Appointment)
admin.site.register(Negotiation)

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.generic import View, FormView, TemplateView, ListView
from django.forms.utils import ErrorList
from django.http import HttpResponse

from accounts.models import User, Staff
from bookings.bookings_core.models import Booking
from venues.models import Studio
from studios.studios_web.forms import StudioStaffSignUpForm, StudioStaffSignInForm
from slicerepublic.dateutil import utcnow_millis, utcnow, make_utc
from slicerepublic.sendmail import send_studio_staff_signup_verification_mail
from django.shortcuts import render
from datetime import datetime
import hashlib
import json


# class StudioStaffSignUpView(View):
# form_class = StudioStaffSignUpForm
#     template_name = 'studios/StudioStaffSignUp.html'
#
#     def get(self, request, *args, **kwargs):
#         print(request.GET.get('name'))
#         form = self.form_class()
#         return render(request, self.template_name, {'form': form})

class StudioHome(TemplateView):
    template_name = 'studios/home.html'


class StudioStaffSignUpView(SuccessMessageMixin, FormView):
    template_name = 'studios/StudioStaffSignUp.html'
    form_class = StudioStaffSignUpForm
    success_url = '/studios/signup/'

    def form_valid(self, form):
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            home_studio = form.cleaned_data.get('studios')
            hash_object = hashlib.md5(bytes(str(utcnow_millis()), encoding='utf-8'))

            count = User.objects.get_count_by_email(email=email)

            if count == 1:
                errors = form._errors.setdefault('__all__', ErrorList())
                errors.append('User with the email already exists.')
                return self.form_invalid(form)

            user = User.objects.create_user(email=email,
                                            is_active=False,
                                            password=password,
                                            verification_hash=hash_object.hexdigest())

            staff = Staff(user=user, mbo_site_id=home_studio.mbo_site_id)
            staff.save()

            send_studio_staff_signup_verification_mail(email, hash_object.hexdigest, home_studio.contact_email)

            print(hash_object.hexdigest())
            success_message = "Your account has been made, owner needs to verify it by clicking the activation link " \
                              "that has been sent to his email."
            messages.add_message(self.request, messages.SUCCESS, success_message)
            return super(StudioStaffSignUpView, self).form_valid(form)


class SignUpVerificationView(SuccessMessageMixin, TemplateView):
    template_name = 'studios/Verify.html'

    def get(self, request, *args, **kwargs):
        email = request.GET.get('email')
        verification_hash = request.GET.get('hash')

        if not email or not verification_hash:
            error_message = 'Invalid approach, please use the link that has been sent to your email.'
            messages.add_message(self.request, messages.ERROR, error_message)
            return super(SignUpVerificationView, self).get(request, *args, **kwargs)

        user = User.objects.get_user_by_email_and_verification_hash(email, verification_hash)

        if not user:
            error_message = 'Invalid approach, please use the link that has been sent to your email.'
            messages.add_message(self.request, messages.ERROR, error_message)
            return super(SignUpVerificationView, self).get(request, *args, **kwargs)

        user.is_active = True
        user.save()

        success_message = 'The account has been activated, staff user can now login.'
        messages.add_message(self.request, messages.SUCCESS, success_message)

        return super(SignUpVerificationView, self).get(request, *args, **kwargs)


class StudioStaffLoginView(View):

    def post(self, request):
        login_form = StudioStaffSignInForm(request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data.get('email')
            password = login_form.cleaned_data.get('password')
            home_studio = login_form.cleaned_data.get('studios')

            user = User.objects.get_user_by_email(email)
            if not user or not check_password(password, user.password):
                response_data = {}
                response_data['code'] = 400
                response_data['message'] = 'Invalid credentials.'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            if not user.is_active:
                response_data = {}
                response_data['code'] = 400
                response_data['message'] = 'Pending verification by the owner of the studio.'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            user = authenticate(email=email, password=password)
            login(request, user)
        else:
            errors = login_form.errors
            response_data = {}
            response_data['code'] = 400

            message = ""
            if 'email' in errors.keys():
                message += errors['email'][0]

            if 'password' in errors.keys():
                if message != "":
                    message += "<br>"
                message += errors['password'][0]

            if 'studios' in errors.keys():
                if message != "":
                    message += "<br>"
                message += errors['studios'][0]

            response_data['message'] = message
            return HttpResponse(json.dumps(response_data), content_type="application/json")

        response_data = {}
        response_data['code'] = 200
        response_data['message'] = 'Success'
        return HttpResponse(json.dumps(response_data), content_type="application/json")


class ViewBookings(ListView):
    model = Booking
    template_name = "studios/bookings.html"
    context_object_name = "bookings"

    def get_queryset(self):
        mbo_site_id = self.get_mbo_site_id()
        from_date = self.get_from_date()
        to_date = self.get_to_date()

        if not self.request.user.is_anonymous() and not self.request.user.is_superuser:
            user_id = self.request.user.id
            staff = Staff.objects.get_staff_by_user_id(user_id)
            mbo_site_id = staff.mbo_site_id

        qs = Booking.objects.search_bookings(mbo_site_id, from_date, to_date)
        return qs

    def get_context_data(self, **kwargs):
        context = super(ViewBookings, self).get_context_data(**kwargs)
        studios = Studio.objects.all()
        context['studios'] = studios

        studio_map = {}

        for studio in studios:
            studio_map[studio.mbo_site_id] = studio.name

        context['studio_map'] = studio_map

        if self.request.GET.get('location'):
            context['location'] = int(self.request.GET.get('location'))

        if self.request.GET.get('from_date'):
            context['from_date'] = self.request.GET.get('from_date')

        if self.request.GET.get('to_date'):
            context['to_date'] = self.request.GET.get('to_date')

        return context

    def get_mbo_site_id(self):
        location = self.request.GET.get('location')
        mbo_site_id = None
        if location and location != '0':
            studio = Studio.objects.get(pk=location)
            mbo_site_id = studio.mbo_site_id
        return mbo_site_id

    def get_from_date(self):
        from_date = self.request.GET.get('from_date')
        if not from_date:
            from_date = utcnow().date()
        else:
            selected_date = make_utc(datetime.strptime(from_date, '%d/%m/%Y'))
            from_date = selected_date.date()
        return from_date

    def get_to_date(self):
        to_date = self.request.GET.get('to_date')
        if not to_date:
            to_date = utcnow().date()
        else:
            selected_date = make_utc(datetime.strptime(to_date, '%d/%m/%Y'))
            to_date = selected_date.date()
        return to_date
from django.shortcuts import render

from django.contrib.auth import login
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView

import random
import json
import requests
import logging

# from django_user_agents.utils import get_user_agent
from django.contrib.auth import get_user_model
from .forms import RegistrationForm
from users.models import User
from datetime import datetime

logging.basicConfig(filename="registration_error.log", level=logging.INFO)


User = get_user_model()


class AuthView(FormView):
    form_class = RegistrationForm
    template_name = 'index.html'

    def get_success_url(self):
        self.success_url = reverse('users:cpanel')

    def post(self, *args, **kwargs):
        self.email = self.request.POST.get('email')
        self.phone = self.request.POST.get('phone')
        print('post')
        print('create')
        user = User.objects.create(username=self.phone, email=self.email)
        user.save()
        response = HttpResponse(status=200)
        return response

    def get(self, *args, **kwargs):
        print('get')
        if self.request.user.is_authenticated:
            return redirect('users:cpanel')
     
        return super().get(*args, **kwargs)

    def form_valid(self, form):
        self.email = self.request.POST.get('email')
        self.phone = self.request.POST.get('phone')

        # if User.objects.filter(username=phone, is_password_changed=False).exists():
        #     user = User.objects.get(username=phone)
        #     user.set_password('dsa!d21dZ')
        #     user.save()

        #     login(self.request, user)
        #     response = HttpResponse(status=200)
        #     return response

        self.get_context_data(phone=self.phone)
        response = HttpResponse(status=200)
        return response


    def create_user(self, phone, password, **kwargs):
        print('create')
        user = User.objects.create(username=phone, email=self.email)
        user.save()



class Cpanel(FormView):
    form_class = RegistrationForm
    template_name = 'index.html'

    def get(self, *args, **kwargs):
        print('get')
        if self.request.user.is_authenticated:
            return redirect('users:cpanel')
     
        return super().get(*args, **kwargs)


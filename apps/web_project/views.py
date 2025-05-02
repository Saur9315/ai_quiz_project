from django.shortcuts import render, redirect
from django.views.generic import TemplateView, DetailView, UpdateView
from .forms import UserRegistrationForm
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.http import Http404
from .forms import CustomUserChangeForm


User = get_user_model()


class HomePageView(TemplateView):
    template_name = 'home.html'


class RegisterView(FormView):
    template_name = 'register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    

@method_decorator(login_required, name='dispatch')
class ProfileView(DetailView):
    model = User
    template_name = 'profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user


@method_decorator(login_required, name='dispatch')
class ProfileEditView(UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'profile_edit.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj != self.request.user:
            raise Http404("Вы не можете редактировать этот профиль")
        return obj

    
    
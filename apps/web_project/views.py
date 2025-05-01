from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .forms import UserRegistrationForm
from django.views.generic.edit import FormView
from django.urls import reverse_lazy



class HomePageView(TemplateView):
    template_name = 'home.html'


class RegisterView(FormView):
    template_name = 'register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')  # Переадресация на страницу логина после успешной регистрации

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

# def register(request):
#     if request.method == 'POST':
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('login')
#     else:
#         form = UserRegistrationForm()
#     return render(request, 'register.html', {'form': form})

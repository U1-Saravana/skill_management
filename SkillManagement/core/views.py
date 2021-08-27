from django.forms.models import inlineformset_factory
from django.views.generic.base import ContextMixin
from core.models import User, Skills
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import View, TemplateView
from django.http import HttpResponseRedirect,  JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

from .forms import LoginForm, EmployeeCreateForm, SkillForm, SkillsForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.core.serializers import serialize

from .models import Skills


def home(request):
    if request.user.is_authenticated:
        if request.user.is_manager:
            return redirect('employee_list')
        else:
            return redirect('skills_list')
    form = LoginForm()
    return render(request, 'login.html', {'form': form})


class LoginView(View):
    form_class = LoginForm
    template_name = 'login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        err_msg = 'Invalid credentials.'

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse_lazy('home'))
                else:
                    return HttpResponseRedirect(reverse_lazy('login'))
            else:
                return render(request, self.template_name, {'form': form, 'error': err_msg})
        else:
            return render(request, self.template_name, {'form': form, 'error': err_msg})


class Overview(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        request.session['emp_id'] = self.kwargs.get("id")
        skills_list = Skills.objects.filter(user_id=self.kwargs.get("id"))
        context = {}
        context['skills_list'] = skills_list
        return render(request, 'employee_overview.html', context)

    def test_func(self):
        return self.request.user.is_manager


class ChartData(View):
    def post(self, request, *args, **kwargs):
        chart_data = list(Skills.objects.filter(user_id=self.kwargs.get("id")).extra(
            select={'name': 'skill_name', 'value': 'score'}).values('name', 'value'))
        return JsonResponse(chart_data, safe=False)


class SkillsListView(LoginRequiredMixin, ListView):
    model = Skills
    context_object_name = 'skills_list'
    template_name = 'skills_list.html'

    def get_queryset(self):
        return self.model.objects.filter(user_id=self.request.user.id)


class SkillsCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'skills_add.html'
    login_url = 'login'

    def test_func(self):
        return self.request.user.is_manager or not self.request.user.is_manager

    def get(self, request):
        return render(request, self.template_name, {"form": SkillForm()})

    def post(self, request, *args, **kwargs):
        form = SkillForm(request.POST or None)
        if request.session.get('emp_id',None):
            reverse_url = reverse_lazy('overview',kwargs={'id': request.session['emp_id']},)
            user = User.objects.get(id=request.session['emp_id'])
        else:
            user = request.user  
            reverse_url =  reverse_lazy('skills_list') 

        if form.is_valid():
            skill = Skills.objects.create(
                user=user,
                skill_name=form.cleaned_data['skill_name'],
                score=form.cleaned_data['score']
            )
            return HttpResponseRedirect(reverse_url)
        return render(request, 'skills_add.html', {'form': form})


class SkillUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Skills
    form_class = SkillsForm
    template_name = "skills_add.html"

    def test_func(self, *args, **kwargs):
        if self.request.user.is_manager:
            return True
        return self.request.user.id == Skills.objects.get(id=self.kwargs.get("id")).user_id

    def get_object(self):
        id = self.kwargs.get("id")
        return get_object_or_404(Skills, id=id)

    def post(self, request, *args, **kwargs):
        form = SkillsForm(request.POST, instance=Skills.objects.get(
            id=self.kwargs.get("id")))

        if self.request.user.is_manager:
               reverse_url = reverse_lazy('overview',kwargs={'id': request.session['emp_id']})
               user = User.objects.get(id=request.session['emp_id'])
        else:
            reverse_url =  reverse_lazy('skills_list')  
            user = request.user
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = user
            obj.save()
            return HttpResponseRedirect(reverse_url)
        return render(request, 'skills_add.html', {'form': form})


class SkillDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Skills
    success_url = reverse_lazy("skills_list")

    def test_func(self, *args, **kwargs):
        if self.request.user.is_manager:
            return True
        return self.request.user.id == Skills.objects.get(id=self.kwargs.get("pk")).user_id

    def get(self, request, *args, **kwargs):
        if self.request.user.is_manager:
            self.success_url = reverse_lazy('overview',kwargs={'id': request.session['emp_id']})
        return self.post(request, *args, **kwargs)


class EmployeeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    success_url = reverse_lazy("employee_list")

    def test_func(self, *args, **kwargs):
        return self.request.user.is_manager
        
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class EmployeeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    form_class = EmployeeCreateForm
    model = User
    template_name = 'employee_register.html'
    login_url = 'login'

    def test_func(self):
        return self.request.user.is_manager

    def post(self, request):
        form = EmployeeCreateForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.save()
            return HttpResponseRedirect(reverse_lazy('employee_list'))
        return render(request, 'employee_register.html', {'form': form})


class EmployeeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    context_object_name = 'emp_list'
    queryset = User.objects.exclude(is_manager=True).order_by(
        '-date_joined').only('username')
    template_name = 'employee_list.html'

    def test_func(self):
        return self.request.user.is_manager


class EmployeeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = EmployeeCreateForm
    template_name = "employee_register.html"

    def get_object(self):
        id = self.kwargs.get("id")
        return get_object_or_404(User, id=id)

    def post(self, request, *args, **kwargs):
        form = EmployeeCreateForm(
            request.POST, instance=User.objects.get(id=self.kwargs.get("id")))
        if form.is_valid():
            obj = form.save()
            obj.save()
            return HttpResponseRedirect(reverse_lazy('employee_list'))
        return render(request, 'employee_register.html', {'form': form})

    def test_func(self):
        return self.request.user.is_manager


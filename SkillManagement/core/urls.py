from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home, name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('emp_register/', EmployeeCreateView.as_view(), name='register'),
    path('emp_list/', EmployeeListView.as_view(), name='employee_list'),
    path('emp_update/<int:id>/', EmployeeUpdateView.as_view(),
         name='employee_update'),
    path('emp_rm/<int:pk>/', EmployeeDeleteView.as_view(), name='employee_delete'),
    path('chartdata/<int:id>/', ChartData.as_view(), name="chartdata"),


    path('overview/<int:id>', Overview.as_view(), name='overview'),
    path('skills/', SkillsListView.as_view(), name='skills_list'),
    path('skills/add/', SkillsCreateView.as_view(), name='skills_add'),
    path('skills/<int:id>/', SkillUpdateView.as_view(), name='skills_update'),
    path('skill/rm/<int:pk>/', SkillDeleteView.as_view(), name='skill_delete')


]

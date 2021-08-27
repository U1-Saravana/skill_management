from django import forms
from django.forms import widgets
from .models import User, Skills
from django.contrib.auth.hashers import make_password


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100, required=True, widget=forms.TextInput(attrs={'id': 'username', 'name': 'username',
                                                                                                              }))
    password = forms.CharField(label='Password', required=True, max_length=100, widget=forms.PasswordInput(attrs={'id': 'password', 'name': 'password',
                                                                                                                  }))


class EmployeeCreateForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'confirm_pswd', 'required': 'true',
                                                                         }))

    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'id': 'user_name', 'required': 'true',
                                               }),
            'password': forms.PasswordInput(attrs={'id': 'password', 'required': 'true', })}
        labels = {
            'username': '',
        }

    def clean(self):
        super(EmployeeCreateForm, self).clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if len(username) < 4:
            self._errors['username'] = self.error_class([
                'Username Minimum 4 characters required'])

        if password != confirm_password:
            self._errors['password'] = self.error_class([
                "Password and Confirm password does not match"])

        if len(password) < 4:
            self._errors['password'] = self.error_class([
                'Password Should Contain a minimum of 6 characters'])

        return self.cleaned_data

    def save(self):
        user = super(EmployeeCreateForm, self).save(commit=False)
        user.password = make_password(self.cleaned_data['password'])
        user.save()
        return user


class SkillsForm(forms.ModelForm):
    class Meta:
        model = Skills
        exclude = ('user',)
        widgets = {
            'skill_name': forms.TextInput(attrs={'id': 'skill_name',
                                                 'onchange': 'default_state(this)', 'name': 'skill_name', 'type': 'text',
                                                 }),
            'score': forms.TextInput(attrs={
                'id': 'score', 'onchange': 'default_state(this)', 'type': 'range', 'name': 'score', 'min': '1', 'max': '100'}),
        }

    def clean(self):
        super(SkillsForm, self).clean()
        score = self.cleaned_data.get('score')
        skill_name = self.cleaned_data.get('skill_name')

        if len(skill_name) == 0:
            self._errors['skill_name'] = self.error_class([
                'Minimum 1 characters required'])

        return self.cleaned_data


class SkillForm(forms.Form):
    score = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'id': 'score', 'onchange': 'default_state(this)', 'type': 'range', 'name': 'score', 'min': '1', 'max': '100'}))

    skill_name = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'id': 'skill_name',
                                                                                              'onchange': 'default_state(this)', 'name': 'skill_name', 'type': 'text',
                                                                                              }))

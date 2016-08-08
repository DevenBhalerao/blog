from django import forms
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("This user does not exist")

        if not user.check_password(password):
            raise forms.ValidationError("Incorrect password")

        return super(UserLoginForm, self).clean(*args, **kwargs)


class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(label='Email address')
    email2 = forms.EmailField(label='Confirm Email')
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label='Confirm Password'
                                )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'email2',
            'password',
            'password2'
        ]

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        email2 = self.cleaned_data.get('email2')
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if email != email2:
            raise forms.ValidationError("Emails must match")
        if password != password2:
            raise forms.ValidationError("Passwords must match")
        email_qs = User.objects.filter(email=email)
        if email_qs.exists():
            raise forms.ValidationError(
                "This email has already been registered"
            )
        return super(UserRegisterForm, self).clean(*args, **kwargs)


class ChangePasswordForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_new = forms.CharField(widget=forms.PasswordInput)
    password_new_confirm = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        logger.debug("init called")
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        logger.debug("hmmmm")
        password = self.cleaned_data.get('password')
        username = self.cleaned_data.get('username')
        logger.debug("{0} by 'clean'".format(self.request))
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("This user does not exist")

        if not user.check_password(password):
            raise forms.ValidationError("Incorrect password")

        password_new = self.cleaned_data.get('password_new')
        password_new_confirm = self.cleaned_data.get('password_new_confirm')
        if password_new != password_new_confirm:
            raise forms.ValidationError("Passwords must match")
        return super(ChangePasswordForm, self).clean(*args, **kwargs)

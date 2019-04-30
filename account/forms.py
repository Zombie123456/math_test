from django import forms
from captcha.fields import CaptchaField


class VerificationCodeForm(forms.Form):

    verification_code = CaptchaField()

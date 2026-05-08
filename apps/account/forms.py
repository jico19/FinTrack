from django import forms
from django.contrib.auth.models import User




from .models import UserProfile

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_pic', 'budget']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-gray-50 p-3', 
                'rows': 3,
                'placeholder': 'Tell us about your financial goals...'
            }),
            'profile_pic': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition-colors'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-gray-50 p-3',
                'placeholder': '0.00'
            }),
        }

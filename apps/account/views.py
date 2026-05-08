from django.views.generic import CreateView, TemplateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import UserProfile, UserChallengeProgress
from . import forms
from apps.tracker.services import get_monthly_summary
from datetime import date

def logout_view(request):
    logout(request)
    return redirect('login')

class RegisterView(CreateView):
    template_name = 'account/register.html'
    success_url = reverse_lazy('login')
    form_class = forms.RegisterForm

    def form_valid(self, form):
        data = form.cleaned_data
        User.objects.create_user(
            username=data.get('username'),
            password=data.get('password')
        )
        return redirect('login')

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "account/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.kwargs.get('pk') and get_object_or_404(User, pk=self.kwargs.get('pk')) or self.request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        
        # Get active challenges and calculate percentage
        challenges_progress_raw = UserChallengeProgress.objects.filter(
            user=user, 
            challenge__is_active=True
        ).select_related('challenge')
        
        challenges_progress = []
        for cp in challenges_progress_raw:
            percent = (cp.current_count / cp.challenge.target_count * 100) if cp.challenge.target_count > 0 else 0
            challenges_progress.append({
                'obj': cp,
                'percent': min(percent, 100)
            })
            
        # F-02: Monthly Money Summary
        today = date.today()
        income, expense, balance = get_monthly_summary(user, today.year, today.month)
            
        context.update({
            "profile": profile,
            "challenges_progress": challenges_progress,
            "monthly_summary": {
                "income": income,
                "expense": expense,
                "balance": balance,
                "month_name": today.strftime('%B %Y')
            }
        })
        return context

class EditProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = forms.UserProfileForm
    template_name = "account/edit_profile.html"

    def get_object(self, queryset=None):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def get_success_url(self):
        return reverse_lazy('profile_view', kwargs={'pk': self.request.user.pk})

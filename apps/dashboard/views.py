from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    TemplateView, 
    UpdateView, 
    DeleteView, 
    DetailView
)   
from apps.tracker.models import BudgetRecord
from django.contrib.auth.mixins import LoginRequiredMixin



class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'tracker/dashboard.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super().get_context_data(**kwargs)
        context["records"] = BudgetRecord.objects.filter(user=self.request.user)
        return context

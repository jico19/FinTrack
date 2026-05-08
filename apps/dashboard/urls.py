from django.urls import path
from . import views

urlpatterns = [
    # Legacy view, we are using apps.tracker.views.dashboard now as the main functional view
    path('legacy-dashboard/', views.HomePageView.as_view(), name="legacy_dashboard"),
]

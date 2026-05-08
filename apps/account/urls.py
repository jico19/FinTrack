from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('profile/<int:pk>/', views.ProfileView.as_view(), name="profile_view"),
    path('profile/edit/', views.EditProfileView.as_view(), name="edit-profile"),
    path('', LoginView.as_view(template_name="account/login.html"), name="login"),
    path('register/', views.RegisterView.as_view(), name="register"),
    path('logout/', views.logout_view, name="logout")
]

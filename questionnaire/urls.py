from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.questionnaire_view, name='questionnaire'),
    path('thank-you/', views.thank_you_view, name='thank_you'),
    path('login/', views.custom_login, name='custom_login'),  # User login page
    path('logout/', views.custom_logout, name='custom_logout'),  # Logout functionality
    path('guests/', views.guest_info, name='guest_info'),  # Guest info page (protected)
    path('guests/<int:pk>/', views.guest_detail, name='guest_detail'),  # new
    path('analysis/', views.satisfaction_analysis, name='satisfaction_analysis'),
    path('analysis/download/pdf/', views.download_pdf, name='download_pdf'),
    path('analysis/download/excel/', views.download_excel, name='download_excel'),


]

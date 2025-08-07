"""
URL patterns for demo app.
"""
from django.urls import path
from . import views

app_name = 'demo'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('features/', views.FeaturesView.as_view(), name='features'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('styles/bootstrap/', views.StyleBootstrapView.as_view(), name='style-bootstrap'),
    path('styles/tailwind/', views.StyleTailwindView.as_view(), name='style-tailwind'),
    path('styles/vanilla/', views.StyleVanillaView.as_view(), name='style-vanilla'),
]
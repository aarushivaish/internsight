
from django.urls import include, path
from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path('home/', views.home, name='home'),
    path('listings/', views.listings, name='listings'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('recommended/', views.recommended_listings, name='recommended'),
]

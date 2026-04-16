from django.urls import path
from .views import (
    dashboard,
    home,
    login_view,
    logout_view,
    register,
    upload_resume,
)

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('upload/', upload_resume, name='upload_resume'),
]
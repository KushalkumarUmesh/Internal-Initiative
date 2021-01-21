from django.urls import path
from .import views
from django.contrib.auth import views as auth_views

urlpatterns=[
    path('home/',views.home,name='Home'),
    path('',views.index,name='Index'),
    path('create_new_project/',views.create_new_project,name='create_new_project'),
    path('edit_existing_project/',views.edit_existing_project,name='edit_existing_project'),
    path('update_tracker/',views.update_tracker,name='update_tracker'),
    path('login/',auth_views.LoginView.as_view(template_name='reviewApp/loginD.html'),name='login'),
    path('logout/',auth_views.LogoutView.as_view(template_name='reviewApp/logoutD.html'),name='logout'),

]
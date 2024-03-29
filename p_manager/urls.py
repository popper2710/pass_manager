from django.urls import path
from .import views


app_name = 'p_manager'
urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.auth_login, name='login'),
    path('logout/', views.auth_logout, name='logout'),
    path('index/', views.index, name='index'),
    path('change_user/', views.UserUpdateView.as_view(), name='update_user'),
    path('update/<pk>', views.PasswordUpdateView.as_view(), name="update"),
    path('create/', views.create_new_password, name='create_pass'),
    path('add/', views.add_pass, name='add_pass')
]

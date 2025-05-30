from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('evaluation/', views.evaluation_list, name='evaluation_list'),
    path('evaluation/<int:reap_id>/', views.evaluation_form, name='evaluation_form'),
    path('evaluation/<int:reap_id>/user/<int:user_id>/', views.evaluation_form, name='evaluation_form'),
    path('evaluation/<int:reap_id>/user/<int:user_id>/<int:dotted_manager_id>/', views.evaluation_form, name='evaluation_form'),
] 
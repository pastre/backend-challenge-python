from django.urls import path

from . import views

urlpatterns = [
	path('onAnswer', views.onAnswer, name='onAnswer'),
]
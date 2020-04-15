from django.urls import path

from . import views

urlpatterns = [
	path('reflections/<int:name>', views.reflections, name='reflections'),
	path('reflections', views.reflections, name='reflections'),
]
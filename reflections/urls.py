from django.urls import path

from . import views

urlpatterns = [
	path('reflections/<int:reflectionId>', views.reflections, name='reflections'),
	path('reflections/<int:reflectionId>/share', views.shareReflection, name='shareReflection'),
	path('reflections', views.reflections, name='reflections'),

	path('users', views.users, name='users'),
	path('users/<int:userId>', views.users, name='users'),


	path('auth', views.auth, name='auth'),

	path('logout', views.logout, name='logout'),
]
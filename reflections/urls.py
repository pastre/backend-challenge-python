from django.urls import path

from . import views

urlpatterns = [
	path('reflections/<int:reflectionId>', views.reflections, name='reflections'),
	path('reflections/<int:reflectionId>/share', views.shareReflection, name='shareReflection'),
	path('reflections', views.reflections, name='reflections'),

	path('users', views.users, name='users'),
	path('users/<int:userId>', views.users, name='user'),
	path('users/<int:userId>/reflections', views.userReflections, name='userReflections'),


	path('auth', views.auth, name='auth'),

	path('logout', views.logout, name='logout'),
]
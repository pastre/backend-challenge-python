from django.http import HttpResponse
from django.core import serializers

from  .models import *


def reflections(request, name = None):
	if name == None:
		if request.method != 'GET': return HttpResponseForbidden('Wrong method, sorry')

		serialized = serializers.serialize('json', Reflection.objects.all())
		return HttpResponse(serialized)
		
	return HttpResponse(f'<h1>NOME TOSCO {name}</h1>')
from django.http import HttpResponse
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from  .models import *


def formattedModel(m):

		serialized = serializers.serialize('json', m)
		return HttpResponse(serialized)

def reflections(request, reflectionId = None):
	if reflectionId == None:
		if request.method != 'GET': return HttpResponseForbidden('Wrong method, sorry')

		return formattedModel(Reflection.objects.all())

	if request.method == 'GET':
		try:
			reflection = Reflection.objects.get(pk=reflectionId).first()
			return formattedModel(reflection)
		except ObjectDoesNotExist:
			return HttpResponse(f'PEGUEI')

	return HttpResponse(f'<h1>NOME TOSCO {reflectionId}</h1>')
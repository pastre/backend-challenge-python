from django.http import HttpResponse
from django.http import HttpResponse, HttpResponseForbidden
from django.http import QueryDict

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

from  .models import *

import json


def formattedModel(m):

		serialized = json.dumps(m.toDict())
		return HttpResponse(serialized)

def getAllReflections(): 
	asDict = [ i.toDict() for i in Reflection.objects.all()]

	serialized = json.dumps(asDict)
	return HttpResponse(serialized)

def deleteReflection(reflectionId): pass # TODO
def updateReflection(reflectionId, newReflection): pass # TODO

def getReflection(reflectionId):
		try:
			reflection = Reflection.objects.get(pk=reflectionId)
			return formattedModel(reflection)

		except ObjectDoesNotExist:
			# TODO
			return HttpResponse(f'PEGUEI')

def createReflection(text): 
	newReflection = Reflection(content = text)
	newReflection.save()

	return  getReflection(newReflection.pk)

@csrf_exempt 
def reflections(request, reflectionId = None):
	if reflectionId == None: 
		if request.method == 'GET': return getAllReflections()
		if request.method == 'DELETE': return deleteReflection(reflectionId) # TODO
		if request.method == 'POST': 

			data = request.POST
			content = data.get('content')

			return createReflection(content) # TODO


		if request.method == 'PUT': pass # TODO

		return HttpResponseForbidden('Wrong method, sorry')
	if request.method == 'GET': # Se tem id e é um GET, 
		return getReflection(reflectionId)


	return HttpResponseForbidden('Wrong method, sorry')
from django.http import HttpResponse
from django.http import HttpResponse, HttpResponseForbidden
from django.http import QueryDict

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

from  .models import *

import json

# Fetches a reflection from the DB
def fetchReflection(reflectionId):
	try:
		reflection = Reflection.objects.get(pk=reflectionId)
		return reflection
	except ObjectDoesNotExist:
		return False

# Formats a reflection from the DB
def formattedModel(m):

		serialized = json.dumps(m.toDict())
		return HttpResponse(serialized)
def returnAllReflections(): 
	asDict = [ i.toDict() for i in Reflection.objects.all()]

	serialized = json.dumps(asDict)
	return HttpResponse(serialized)

# Reflections CRUD
def createReflection(text): 
	newReflection = Reflection(content = text)
	newReflection.save()

	return  getReflection(newReflection.pk)
def getReflection(reflectionId):
	reflection = fetchReflection(reflectionId)

	if not reflection: return HttpResponse(f'PEGUEI')

	return formattedModel(reflection)
def updateReflection(reflectionId, newReflection): pass # TODO
def deleteReflection(reflectionId): 
	reflection = fetchReflection(reflectionId)
	if not reflection: return HttpResponse(f'PEGUEI')

	reflection.delete()

	return returnAllReflections()

@csrf_exempt 
def reflections(request, reflectionId = None):
	if reflectionId == None: 
		if request.method == 'GET': return returnAllReflections()
		if request.method == 'POST': return createReflection(request.POST.get('content'))
		
		return HttpResponseForbidden('Wrong method, sorry')

	if request.method == 'GET': return getReflection(reflectionId)
	if request.method == 'DELETE': return deleteReflection(reflectionId) # TODO
	if request.method == 'PUT': pass # TODO
		
		

	return HttpResponseForbidden('Wrong method, sorry')
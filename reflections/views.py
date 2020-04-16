from django.http import HttpResponse
from django.http import HttpResponse, HttpResponseForbidden
from django.http import QueryDict

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

from django.db.utils import IntegrityError 
from  .models import *

import json
import datetime

def wrongMethod(): return HttpResponseForbidden('Wrong method, sorry')
def malformedRequest(): return HttpResponse(f'malformedRequest')
def error(message): return HttpResponse(json.dumps({"error": message}))
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
def formattedReflections(reflections): 
	asDict = [ i.toDict() for i in reflections]

	serialized = json.dumps(asDict)
	return HttpResponse(serialized)

def reflectionsInRange(params):

	if not 'from' in params.keys(): return malformedRequest()

	start = datetime.datetime.strptime(params["from"][0], "%d%m%Y")
	# start = stringToDatetime(params["from"][0])

	if "to" in params.keys(): end = datetime.datetime.strptime(params["to"][0] + " 23:59:59", "%d%m%Y %H:%M:%S")
	else: end = datetime.datetime.now()

	print("Range: ", start, end)
	reflections = Reflection.objects.filter(createdAt__range = (start, end))

	print(reflections)
	return formattedReflections(reflections)


# Reflections CRUD
def createReflection(text): 
	newReflection = Reflection(content = text)
	newReflection.save()

	return  getReflection(newReflection.pk)
def getReflection(reflectionId):
	reflection = fetchReflection(reflectionId)

	if not reflection: return malformedRequest()

	return formattedModel(reflection)
def updateReflection(reflectionId, newReflection): pass # TODO
def deleteReflection(reflectionId): 
	reflection = fetchReflection(reflectionId)
	if not reflection: return malformedRequest()

	reflection.delete()

	return formattedReflections(Reflection.objects.all())

@csrf_exempt 
def reflections(request, reflectionId = None):
	
	if reflectionId == None: 
		if request.method == 'GET': 
			params = dict(request.GET)
			if len(params.keys()) == 0: return formattedReflections(Reflection.objects.all())
			return reflectionsInRange(params)

		if not 'content' in request.POST.keys(): return malformedRequest()
		if request.method == 'POST': return createReflection(request.POST.get('content'))
		
		return wrongMethod()

	if request.method == 'GET': return getReflection(reflectionId)
	if request.method == 'DELETE': return deleteReflection(reflectionId) # TODO
	if request.method == 'PUT': pass # TODO
		
		

	return wrongMethod()


@csrf_exempt 
def users(request):
	# Se nao for post, retorne erro
	if request.method != 'POST'	: return wrongMethod()
	payload = request.POST
	required = ['username', 'email', 'password',]
	
	# Se esta faltando algum parametro, retorne erro
	for req in required: 
		if not req in payload.keys(): return malformedRequest()

	username, email, password = [payload.get(i) for i in required]
	
	try:
		user = User.objects.create_user(username = username, email=email, password=password )
		user.save()

		return formattedModel(user)
	except IntegrityError: return error("User already exists")




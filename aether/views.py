from django.shortcuts import render

from django.http import HttpResponse
from django.http import HttpResponse, HttpResponseForbidden

from django.core.mail import send_mail

from .models import *

import json
import datetime


def payload(message, status):
	return HttpResponse(
		json.dumps( {"status": status, "payload": message} if not message == None else { "status": status } )
	) 
def onAnswer(request):

	try: 
		mail = request.GET.get('email')
		entry = Email(content = mail)
		entry.save()
	except: 
		print("PORRA BROW")
		pass
	
	return payload(None, "success")

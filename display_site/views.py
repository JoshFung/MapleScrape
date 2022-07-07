from django.http import HttpResponse

from django.shortcuts import render
from django.views import generic

from django.template import loader


def index(request):
    template = loader.get_template('home/index.html')
    return HttpResponse(template.render())

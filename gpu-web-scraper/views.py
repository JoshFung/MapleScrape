from django.http import HttpResponse

from django.shortcuts import render
from django.views import generic

from django.template import loader

from scraping.models import Product


class HomePageView(generic.ListView):
    template_name = 'home.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.all()

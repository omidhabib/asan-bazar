from django.shortcuts import render
from django.views.generic import TemplateView

class SupportView(TemplateView):
    template_name = 'support.html'

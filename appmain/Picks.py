# myclub_root\myclub_site\contact.py
from django import forms
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect


class PickForm(forms.Form):
   user = forms.CharField(max_length=10, label = 'User ID')
   week = forms.CharField(max_length=10, label = 'Week No')
   points = forms.IntegerField(max_value=100,min_value=1,label='Points Game Value')
   koth = forms.CharField(required=False,max_length=20,label='King of the Hill Team')


def contact(request):
    submitted = False
    if request.method == 'POST':
        form = PickForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # assert False
            return HttpResponseRedirect('/picks/form?submitted=True')
    else:
        form = PickForm()
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'appmain/pick_form.html', {'form': form, 'submitted': submitted})
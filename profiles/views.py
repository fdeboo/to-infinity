from django.shortcuts import render
from django.views.generic import FormView
# Create your views here.


class ProfileView(FormView):
    """ A view that renders a user's profile information and order history """

    template_name = 'profiles/profile.html'

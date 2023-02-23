from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from . models import Customer


def user_is_moderator(function):

    def wrap(request, *args, **kwargs):   

        if request.user.user_type == Customer.VENDOR and request.user.is_vendor == True:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrap


def user_is_vendor(function):

    def wrap(request, *args, **kwargs):   

        if request.user.user_type == Customer.VENDOR:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrap


def user_is_custodian(function):

    def wrap(request, *args, **kwargs):    

        if request.user.is_staff:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrap


def user_is_officer(function):

    def wrap(request, *args, **kwargs):    

        if (request.user.user_type == Customer.INITIATOR or request.user.user_type == Customer.OFFICER or request.user.user_type == Customer.HEAD) and request.user.is_staff == True and request.user.is_active == True:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrap


def user_is_procurement_head(function):

    def wrap(request, *args, **kwargs):    

        if request.user.user_type == Customer.HEAD and request.user.is_staff and request.user.is_active == True and request.user.is_stakeholder == True:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrap

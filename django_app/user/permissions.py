from django.shortcuts import get_object_or_404

from rest_framework.permissions import BasePermission

from .models import User


class OwnerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return request.user == obj.user
        else:
            return request.user == obj


class OwnerUrlPermission(BasePermission):
    def has_permission(self, request, view):
        try:
            upk = request.parser_context['kwargs']['upk']
        except KeyError:
            return False

        user = get_object_or_404(User, id=upk)

        return request.user == user

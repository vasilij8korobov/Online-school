from rest_framework import permissions


class IsAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderators').exists()

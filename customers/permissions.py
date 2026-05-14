from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    message = "Танҳо Admin ин амалро иҷро карда метавонад."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_superuser


class IsOwnerOrAdmin(BasePermission):
    message = "Шумо танҳо маълумоти худро дида метавонед."

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.user == request.user
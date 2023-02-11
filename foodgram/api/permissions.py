from rest_framework import permissions

#
# class IsAuthenticated(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated


# class IsAuthorOrReadOnly(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         if request.method in permissions.SAFE_METHODS and request.user.is_authenticated:
#             return True
#         return obj.author == request.user
        
#     # def has_object_permission(self, request, view, obj):
#     #     return obj.author == request.user

class IsAuthorOrReadOnly(permissions.BasePermission):
    def object_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS 
            or request.user.is_authenticated
            )

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

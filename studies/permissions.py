from rest_framework import permissions


class SubmitterOnlyPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        # We're verifying that the user editing is only adding experiments, editing etc for studies he submitted
        if not obj:
            return False
        elif not obj.submitter == request.user:
            return False
        else:
            return super().has_object_permission(request, view, obj)


class SelfOnlyProfilePermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if not obj:
            return False

        if not obj.user == request.user:
            return False

        return super().has_object_permission(request, view, obj)

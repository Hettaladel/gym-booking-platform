from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """
    Autorise seulement les utilisateurs avec role ADMIN.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'ADMIN'
        )


class IsAdminOrSelf(BasePermission):
    """
    L’utilisateur peut voir/modifier son propre profil,
    l’admin peut voir/modifier tout le monde.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Si admin → ok
        if getattr(request.user, 'role', None) == 'ADMIN':
            return True

        # Sinon → seulement son propre profil
        return obj.id == request.user.id

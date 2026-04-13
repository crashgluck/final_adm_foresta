from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.accounts.models import UserRole


ROLE_LEVEL = {
    UserRole.CONSULTA: 10,
    UserRole.OPERADOR: 20,
    UserRole.ADMINISTRADOR: 30,
    UserRole.SUPERADMIN: 40,
}


def has_role_at_least(user, required_role: str) -> bool:
    if not user or not user.is_authenticated:
        return False
    if getattr(user, 'is_superuser', False):
        return True
    current_level = ROLE_LEVEL.get(getattr(user, 'role', ''), 0)
    required_level = ROLE_LEVEL.get(required_role, 0)
    return current_level >= required_level


class IsRoleAtLeast(BasePermission):
    required_role = UserRole.CONSULTA

    def has_permission(self, request, view):
        return has_role_at_least(request.user, self.required_role)


class IsAdminOrSuperAdmin(IsRoleAtLeast):
    required_role = UserRole.ADMINISTRADOR


class IsOperatorOrAbove(IsRoleAtLeast):
    required_role = UserRole.OPERADOR


class ReadOnlyOrOperator(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return has_role_at_least(request.user, UserRole.CONSULTA)
        return has_role_at_least(request.user, UserRole.OPERADOR)


class RoleBasedActionPermission(BasePermission):
    """
    ViewSet can define required_roles_per_action = {'list': UserRole.CONSULTA, ...}
    """

    def has_permission(self, request, view):
        mapping = getattr(view, 'required_roles_per_action', None)
        if not mapping:
            return bool(request.user and request.user.is_authenticated)

        action = getattr(view, 'action', None)
        required_role = mapping.get(action, mapping.get('*', UserRole.CONSULTA))
        if request.method in SAFE_METHODS and action is None:
            required_role = mapping.get('read', required_role)
        if not has_role_at_least(request.user, required_role):
            return False

        actor_type = getattr(request.user, 'actor_type', '')
        disallowed_mapping = getattr(view, 'disallowed_actor_types_per_action', None)
        if disallowed_mapping:
            disallowed = disallowed_mapping.get(action, disallowed_mapping.get('*', []))
            if actor_type in disallowed:
                return False

        allowed_mapping = getattr(view, 'allowed_actor_types_per_action', None)
        if allowed_mapping:
            allowed = allowed_mapping.get(action, allowed_mapping.get('*', []))
            if allowed and actor_type not in allowed:
                return False

        return True


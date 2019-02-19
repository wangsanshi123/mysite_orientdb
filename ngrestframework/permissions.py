"""this module is specific for NgQueryset of OGM of orientdb"""
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import BasePermission
from auth_management.models import Permission, UserPermission


class DjangoModelPermissions(object):
    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['add_%(model_name)s'],
        'PUT': ['change_%(model_name)s'],
        'PATCH': ['change_%(model_name)s'],
        'DELETE': ['delete_%(model_name)s'],
    }

    authenticated_users_only = True

    def get_required_permissions(self, method, model_cls):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        kwargs = {
            'model_name': model_cls.__name__.lower()
        }

        if method not in self.perms_map:
            raise MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]

    def _queryset(self, view):
        assert hasattr(view, 'get_queryset') \
               or getattr(view, 'queryset', None) is not None, (
            'Cannot apply {} on a view that does not set '
            '`.queryset` or have a `.get_queryset()` method.'
        ).format(self.__class__.__name__)

        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
            assert queryset is not None, (
                '{}.get_queryset() returned None'.format(view.__class__.__name__)
            )
            return queryset
        return view.queryset

    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        if not request.user or (
                not request.user.is_authenticated and self.authenticated_users_only):
            return False

        queryset = self._queryset(view)
        perms = self.get_required_permissions(request.method, queryset.manager.source_class)

        return request.user.has_perms(perms)


class NgDjangoModelPermissions(DjangoModelPermissions):

    def get_required_permissions(self, method, model_cls):
        if method not in self.perms_map:
            raise MethodNotAllowed(method)

        result = [perm if method == 'GET' else "management__" + perm for perm in self.perms_map[method]]
        return result


class DjangoModelPermissionsStricted(DjangoModelPermissions):
    """strict mode:even when get the permission is required"""

    def has_permission(self, request, view):
        self.perms_map["GET"] = ['view_%(model_name)s']
        return super().has_permission(request, view)

    pass


class NgPermissions(BasePermission):
    def has_permission(self, request, view):

        # info:得到类名
        class_name = view.__class__.__name__
        permissions = Permission.objects.filter(bac_recognition=class_name).all()
        # info:通过从权限表里查明是否该是否有对应的权限设定, 再来看用户是否具备该权限,
        # info:这是粗粒度的, 如果权限表没有则通过先
        if permissions:
            u_permissions = UserPermission.objects.filter(permission__in=permissions, user=request.user).all()
            if not u_permissions:
                return False

            if not any([u.management for u in u_permissions]) and request.method.lower() in ("put", "delete", "post"):
                return False

        return True

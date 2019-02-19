from rest_framework_jwt.views import ObtainJSONWebToken
from rest_framework import status
from rest_framework.response import Response


class ObtainPublicToken(ObtainJSONWebToken):
    """该接口用于验证访问cmdb提供给其他部门的公共接口的用户身份，不通过用户中心，但是用户的的is_public的字段必须是true"""

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            if getattr(user, "is_public", None):
                return super().post(request, *args, **kwargs)
            else:
                return Response(data="用户没有权限访问该接口", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


obtain_public_jwt_token = ObtainPublicToken.as_view()

from django.contrib.auth import authenticate, login

# Create your views here.
from rest_framework import status
from rest_framework.response import Response

# class LoginViewSet(CreateModelMixin, generics.GenericAPIView):
# http_method_names = ["post"]

# def create(self, request, *args, **kwargs):
#     username = request.data.get("username")
#     password = request.data.get("password")
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)
#         return Response(data={"info": "登陆成功"}, status=status.HTTP_200_OK)
#     else:
#         # Return an 'invalid login' error message.
#         return Response(data={"info": "登陆失败，用户名或密码错误"})
from rest_framework.views import APIView


class LoginView(APIView):
    """基于session的登陆"""

    def post(self, request):
        username = request.data.get("username", None)
        password = request.data.get("password", None)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response(data={"info": "登陆成功"}, status=status.HTTP_200_OK)
        else:
            # Return an 'invalid login' error message.
            return Response(data={"info": "登陆失败，用户名或密码错误"})

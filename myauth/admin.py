from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import Group

from myauth.models import UserProfile


# Register your models here.
class UserProfileAdmin(ModelAdmin):
    pass


class DepartmenteAdmin(ModelAdmin):
    pass


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.unregister(Group)

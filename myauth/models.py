from django.contrib.auth.models import AbstractUser, Group
from django.db import models


# Create your models here.
class DepartmentPermissions(models.Model):
    """部门权限"""
    name = models.CharField(u"权限名称", max_length=255, help_text=u"权限名称")
    manage_item = models.BooleanField(u'管理权限', default=False, help_text=u"管理权限")
    parent = models.ForeignKey('self', verbose_name=u'父导航', null=True, blank=True, related_name='children',
                               help_text=u'父导航页面')
    operation = models.BooleanField(u'操作权限', default=False, help_text=u'操作权限')
    enabled = models.BooleanField(u"权限是否可用", default=True, help_text=u'权限是否可用')
    codename = models.IntegerField(u"权限ID", help_text=u'如果是导航权限请以10000开始编号,如果是页面权限以40000开始编号')
    is_dir = models.BooleanField('是否为目录菜单', default=False, help_text='是否为目录菜单')
    level = models.IntegerField('菜单层级', null=True, help_text='菜单层级')
    rank = models.IntegerField('层级排序', null=True, help_text='层级排序')

    class Meta:
        verbose_name = u"用户权限"
        verbose_name_plural = u"用户权限"
        unique_together = ('codename',)
        ordering = ('codename',)





class UserProfile(AbstractUser):
    username = models.CharField(u'登录名', max_length=32, unique=True, help_text=u'登录名')
    email = models.EmailField(verbose_name=u'邮箱', max_length=255, help_text=u'邮箱地址')
    is_department_manager = models.BooleanField(verbose_name=u'是否是部门管理员（组长）', default=False, help_text=u'是否是部门管理员（组长）')
    is_public = models.BooleanField(default=0, help_text="是否有权限访问公共接口")


class ModulePermission(models.Model):
    class Meta:
        # 命名为cms设计稿里面对应 '菜单权限' 的地方, 例如用户管理
        permissions = (
            ("sites.site", "网站"),
            ("information.examinfo", u"资讯管理-考试信息"),
            ("information.memberschool", u"资讯管理-会员学校"),
            ("school.school", u"学校管理-学校管理"),
            ("course.course", u"课程管理-课程管理"),
            ("student.student", u"学生管理-学生管理"),
            ("exam.exam", u"考务管理-考试管理"),
            ("exam.room", u"考务管理-考场管理"),
        )

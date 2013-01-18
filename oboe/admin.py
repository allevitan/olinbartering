from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from oboe import models

class UserDataInline(admin.StackedInline):
    model = models.UserData
    can_delete = False
    verbose_name_plural = 'user data'

class UserAdmin(UserAdmin):
    inlines = (UserDataInline,)

class MissiveInline(admin.StackedInline):
    model = models.Missive
    can_delete = False

class BulletinAdmin(admin.ModelAdmin):
    inlines = (MissiveInline,)

class ReplyInline(admin.StackedInline):
    model = models.Reply

class ThreadAdmin(admin.ModelAdmin):
    inlines = (ReplyInline, )

admin.site.register(models.Filter)
admin.site.register(models.Bulletin, BulletinAdmin)
admin.site.register(models.Missive)
admin.site.register(models.UserData)
admin.site.register(models.Reply_Thread, ThreadAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

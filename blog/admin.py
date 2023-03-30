from django.contrib import admin
from .models import *

# Register your models here.
# from mptt.admin import MPTTModelAdmin
# from blogpost.blog.models import Node

# admin.site.register(Node, MPTTModelAdmin)
admin.site.register(Blog)
admin.site.register(IpModel)
admin.site.register(MailBox)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "post", "created", "level")
    list_filter = ("active", "created", "updated")
    search_fields = ("name", "email", "body")

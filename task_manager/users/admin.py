from django.contrib import admin

from task_manager.users.models import CustomUser

admin.site.register(CustomUser)

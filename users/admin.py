from django.contrib.auth import admin as auth_admin
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from users.models import User 
from import_export import resources
from import_export.admin import ExportActionModelAdmin

class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('email')
        exclude = 'id'

@admin.register(User)
class UserAdmin(ExportActionModelAdmin, auth_admin.UserAdmin):
    resource_class = UserResource
    list_display = 'email', 'is_active'

    list_filter = ('is_active', 'is_staff', 'is_superuser', 'email',)

from django.contrib import admin


class CustomAdmin(admin.ModelAdmin):
    change_form_template = 'common/admin/change_form.html'

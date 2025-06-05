from django.contrib import admin
from .models import Department

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department', 'code', 'active', 'created_at', 'created_by', 'updated_at', 'modified_by')
    list_filter = ('active', 'created_at')
    search_fields = ('department', 'code')
    ordering = ('department',)
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'modified_by')

    fieldsets = (
        (None, {
            'fields': ('department', 'code', 'active')
        }),
        ('Información de Auditoría', {
            'fields': ('created_by', 'created_at', 'modified_by', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user.id
        obj.modified_by = request.user.id
        super().save_model(request, obj, form, change)
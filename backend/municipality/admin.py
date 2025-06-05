from django.contrib import admin
from .models import Municipality 
from district.models import District

@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ('municipality', 'code', 'department_name', 'active', 'created_at', 'modified_by')
    list_filter = ('active', 'department', 'created_at')
    search_fields = ('municipality', 'code', 'department__department')
    ordering = ('department__department', 'municipality')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'modified_by')

    fieldsets = (
        (None, {
            'fields': ('municipality', 'code', 'department', 'active')
        }),
        ('Información de Auditoría', {
            'fields': ('created_by', 'created_at', 'modified_by', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def department_name(self, obj):
        return obj.department.department if obj.department else "N/A"
    department_name.short_description = 'Departamento'
    department_name.admin_order_field = 'department__department'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user.id
        obj.modified_by = request.user.id
        super().save_model(request, obj, form, change)
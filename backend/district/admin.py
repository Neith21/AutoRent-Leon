from django.contrib import admin
from district.models import District

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('district', 'code', 'municipality_name', 'department_of_municipality', 'active', 'created_at', 'modified_by')
    list_filter = ('active', 'municipality__department', 'municipality', 'created_at')
    search_fields = ('district', 'code', 'municipality__municipality', 'municipality__department__department')
    ordering = ('municipality__department__department', 'municipality__municipality', 'district')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'modified_by')

    fieldsets = (
        (None, {
            'fields': ('district', 'code', 'municipality', 'active')
        }),
        ('Información de Auditoría', {
            'fields': ('created_by', 'created_at', 'modified_by', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def municipality_name(self, obj):
        return obj.municipality.municipality if obj.municipality else "N/A"
    municipality_name.short_description = 'Municipio'
    municipality_name.admin_order_field = 'municipality__municipality'

    def department_of_municipality(self, obj):
        if obj.municipality and obj.municipality.department:
            return obj.municipality.department.department
        return "N/A"
    department_of_municipality.short_description = 'Departamento (del Municipio)'
    department_of_municipality.admin_order_field = 'municipality__department__department'


    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user.id
        obj.modified_by = request.user.id
        super().save_model(request, obj, form, change)
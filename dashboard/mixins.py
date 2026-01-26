from django.contrib import admin


class ExportCSVMixin:
    """Mixin to add CSV export functionality"""
    
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        import io
        
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        
        writer = csv.writer(response)
        writer.writerow(field_names)
        
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        
        return response
    
    export_as_csv.short_description = "Export Selected as CSV"


class AdminImageWidget(admin.widgets.AdminFileWidget):
    """Custom widget to display images in admin"""
    
    def render(self, name, value, attrs=None, renderer=None):
        from django.utils.html import format_html
        output = []
        if value and hasattr(value, "url"):
            output.append(
                f'<a href="{value.url}" target="_blank">'
                f'<img src="{value.url}" width="150" style="border-radius: 8px; margin-bottom: 10px;" />'
                f'</a>'
            )
        output.append(super().render(name, value, attrs, renderer))
        return format_html(''.join(output))

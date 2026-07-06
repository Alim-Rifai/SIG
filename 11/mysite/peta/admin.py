from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Provinsi, Kabkota, Kecamatan, NamaData, Datprof
from .forms import DatprofAdminForm
from .resources import DatprofResource


class KabkotaInline(admin.TabularInline):
    model = Kabkota
    extra = 0
    fields = ('id', 'name', 'alt_name', 'latitude', 'longitude')


class KecamatanInline(admin.TabularInline):
    model = Kecamatan
    extra = 0
    fields = ('id', 'name', 'alt_name', 'latitude', 'longitude')


@admin.register(Provinsi)
class ProvinsiAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'alt_name', 'latitude', 'longitude')
    search_fields = ('name', 'alt_name')
    list_filter = ('name',)
    list_per_page = 25
    inlines = [KabkotaInline]


@admin.register(Kabkota)
class KabkotaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'alt_name', 'latitude', 'longitude')
    search_fields = ('name', 'alt_name')
    list_filter = ('name',)
    list_per_page = 25
    inlines = [KecamatanInline]


@admin.register(Kecamatan)
class KecamatanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'alt_name', 'latitude', 'longitude')
    search_fields = ('name', 'alt_name')
    list_filter = ('name',)
    list_per_page = 25


@admin.register(NamaData)
class NamaDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'nama')
    search_fields = ('nama',)
    list_per_page = 25


@admin.register(Datprof)
class DatprofAdmin(ImportExportModelAdmin):
    resource_class = DatprofResource
    form = DatprofAdminForm
    list_display = ('id', 'provinsi', 'namadata', 'tahun', 'jumlah')
    search_fields = ('provinsi__name', 'namadata__nama', 'tahun')
    list_per_page = 25


# --- Custom User Admin with last-admin protection (Task 5.3) ---
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.contrib import messages


class CustomUserAdmin(BaseUserAdmin):
    """Custom User admin with last-admin deletion/deactivation protection."""

    def delete_model(self, request, obj):
        """Prevent deletion of the last Administrator."""
        admin_group = Group.objects.filter(name='Administrator').first()
        if admin_group and obj.groups.filter(pk=admin_group.pk).exists():
            admin_count = admin_group.user_set.filter(is_active=True).count()
            if admin_count <= 1:
                messages.error(
                    request,
                    "Cannot delete the last active Administrator. "
                    "At least one active Administrator account must exist."
                )
                return
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """Prevent bulk deletion if it would remove the last Administrator."""
        admin_group = Group.objects.filter(name='Administrator').first()
        if admin_group:
            admin_users_in_selection = queryset.filter(
                groups=admin_group, is_active=True
            )
            total_admins = admin_group.user_set.filter(is_active=True).count()
            remaining = total_admins - admin_users_in_selection.count()
            if remaining < 1:
                messages.error(
                    request,
                    "Cannot delete: this would remove the last active Administrator. "
                    "At least one active Administrator account must exist."
                )
                return
        super().delete_queryset(request, queryset)

    def save_model(self, request, obj, form, change):
        """Prevent deactivation of the last Administrator."""
        if change and not obj.is_active:
            admin_group = Group.objects.filter(name='Administrator').first()
            if admin_group and obj.groups.filter(pk=admin_group.pk).exists():
                active_admins = admin_group.user_set.filter(
                    is_active=True
                ).exclude(pk=obj.pk).count()
                if active_admins < 1:
                    messages.error(
                        request,
                        "Cannot deactivate the last active Administrator. "
                        "At least one active Administrator account must exist."
                    )
                    obj.is_active = True  # Revert the deactivation
        super().save_model(request, obj, form, change)


# Re-register User with custom admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from peta.models import Provinsi, Kabkota, Kecamatan, NamaData, Datprof


class Command(BaseCommand):
    help = 'Create Viewer, Editor, and Administrator groups with appropriate permissions'

    # Models in the peta app that get permissions assigned
    PETA_MODELS = [Provinsi, Kabkota, Kecamatan, NamaData, Datprof]

    def handle(self, *args, **options):
        viewer_group, _ = Group.objects.get_or_create(name='Viewer')
        editor_group, _ = Group.objects.get_or_create(name='Editor')
        admin_group, _ = Group.objects.get_or_create(name='Administrator')

        # Clear existing permissions to ensure idempotency
        viewer_group.permissions.clear()
        editor_group.permissions.clear()
        admin_group.permissions.clear()

        for model in self.PETA_MODELS:
            content_type = ContentType.objects.get_for_model(model)
            permissions = Permission.objects.filter(content_type=content_type)

            for perm in permissions:
                # Viewer: view-only permissions
                if perm.codename.startswith('view_'):
                    viewer_group.permissions.add(perm)
                    editor_group.permissions.add(perm)
                    admin_group.permissions.add(perm)

                # Editor: add + change (no delete)
                elif perm.codename.startswith('add_') or perm.codename.startswith('change_'):
                    editor_group.permissions.add(perm)
                    admin_group.permissions.add(perm)

                # Administrator: all permissions (including delete)
                elif perm.codename.startswith('delete_'):
                    admin_group.permissions.add(perm)

        self.stdout.write(self.style.SUCCESS(
            'Successfully created groups:\n'
            f'  - Viewer: view-only permissions ({viewer_group.permissions.count()} permissions)\n'
            f'  - Editor: view + add + change permissions ({editor_group.permissions.count()} permissions)\n'
            f'  - Administrator: all permissions ({admin_group.permissions.count()} permissions)'
        ))

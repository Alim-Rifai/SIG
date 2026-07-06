from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware

from peta.admin import CustomUserAdmin


def _get_request_with_messages(user=None):
    """Create a request object with message support."""
    factory = RequestFactory()
    request = factory.get('/')
    # Add session middleware
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    # Add messages support
    setattr(request, '_messages', FallbackStorage(request))
    if user:
        request.user = user
    return request


class CustomUserAdminLastAdminProtectionTest(TestCase):
    """Tests for last-admin deletion/deactivation protection."""

    def setUp(self):
        self.admin_group = Group.objects.create(name='Administrator')
        self.admin_user = User.objects.create_user(
            username='admin1', password='testpass123', is_active=True, is_staff=True
        )
        self.admin_user.groups.add(self.admin_group)
        self.regular_user = User.objects.create_user(
            username='regular1', password='testpass123', is_active=True, is_staff=True
        )
        self.superuser = User.objects.create_superuser(
            username='superadmin', password='testpass123'
        )
        self.user_admin = CustomUserAdmin(User, None)

    def test_delete_model_blocks_last_admin(self):
        """Deleting the last active Administrator should be prevented."""
        request = _get_request_with_messages(self.superuser)
        self.user_admin.delete_model(request, self.admin_user)
        # User should still exist
        self.assertTrue(User.objects.filter(pk=self.admin_user.pk).exists())
        # Check error message was added
        stored_messages = list(messages.get_messages(request))
        self.assertEqual(len(stored_messages), 1)
        self.assertIn('Cannot delete the last active Administrator', str(stored_messages[0]))

    def test_delete_model_allows_when_multiple_admins(self):
        """Deleting an admin when there are multiple should succeed."""
        admin2 = User.objects.create_user(
            username='admin2', password='testpass123', is_active=True, is_staff=True
        )
        admin2.groups.add(self.admin_group)

        request = _get_request_with_messages(self.superuser)
        self.user_admin.delete_model(request, self.admin_user)
        # User should be deleted
        self.assertFalse(User.objects.filter(pk=self.admin_user.pk).exists())

    def test_delete_model_allows_non_admin_user(self):
        """Deleting a non-admin user should always succeed."""
        request = _get_request_with_messages(self.superuser)
        self.user_admin.delete_model(request, self.regular_user)
        self.assertFalse(User.objects.filter(pk=self.regular_user.pk).exists())

    def test_delete_queryset_blocks_removing_all_admins(self):
        """Bulk deletion that would remove all admins should be blocked."""
        request = _get_request_with_messages(self.superuser)
        queryset = User.objects.filter(pk=self.admin_user.pk)
        self.user_admin.delete_queryset(request, queryset)
        # User should still exist
        self.assertTrue(User.objects.filter(pk=self.admin_user.pk).exists())
        stored_messages = list(messages.get_messages(request))
        self.assertEqual(len(stored_messages), 1)
        self.assertIn('Cannot delete', str(stored_messages[0]))

    def test_delete_queryset_allows_when_admins_remain(self):
        """Bulk deletion that leaves at least one admin should succeed."""
        admin2 = User.objects.create_user(
            username='admin2', password='testpass123', is_active=True, is_staff=True
        )
        admin2.groups.add(self.admin_group)

        request = _get_request_with_messages(self.superuser)
        queryset = User.objects.filter(pk=self.admin_user.pk)
        self.user_admin.delete_queryset(request, queryset)
        self.assertFalse(User.objects.filter(pk=self.admin_user.pk).exists())

    def test_save_model_blocks_deactivation_of_last_admin(self):
        """Deactivating the last admin should be reverted."""
        request = _get_request_with_messages(self.superuser)
        self.admin_user.is_active = False

        class FakeForm:
            pass

        self.user_admin.save_model(request, self.admin_user, FakeForm(), change=True)
        # is_active should be reverted to True
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_active)
        stored_messages = list(messages.get_messages(request))
        self.assertEqual(len(stored_messages), 1)
        self.assertIn('Cannot deactivate the last active Administrator', str(stored_messages[0]))

    def test_save_model_allows_deactivation_when_multiple_admins(self):
        """Deactivating an admin when others remain should succeed."""
        admin2 = User.objects.create_user(
            username='admin2', password='testpass123', is_active=True, is_staff=True
        )
        admin2.groups.add(self.admin_group)

        request = _get_request_with_messages(self.superuser)
        self.admin_user.is_active = False

        class FakeForm:
            pass

        self.user_admin.save_model(request, self.admin_user, FakeForm(), change=True)
        self.admin_user.refresh_from_db()
        self.assertFalse(self.admin_user.is_active)

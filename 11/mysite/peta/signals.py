from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from peta.models import Provinsi, Kabkota, Kecamatan, NamaData, Datprof, AuditLog

TRACKED_MODELS = [Provinsi, Kabkota, Kecamatan, NamaData, Datprof]


def audit_post_save(sender, instance, created, **kwargs):
    """Create an AuditLog entry when a tracked model is saved."""
    if sender == AuditLog:
        return
    AuditLog.objects.create(
        user=None,  # User tracking handled at admin level
        action='CREATE' if created else 'UPDATE',
        model_name=sender.__name__,
        object_id=str(instance.pk),
        changes={},
    )


def audit_post_delete(sender, instance, **kwargs):
    """Create an AuditLog entry when a tracked model instance is deleted."""
    if sender == AuditLog:
        return
    AuditLog.objects.create(
        user=None,
        action='DELETE',
        model_name=sender.__name__,
        object_id=str(instance.pk),
        changes={},
    )


def connect_signals():
    """Connect audit signals for all tracked models."""
    for model in TRACKED_MODELS:
        post_save.connect(audit_post_save, sender=model)
        post_delete.connect(audit_post_delete, sender=model)

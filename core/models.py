from django.db import models


class BaseManager(models.Manager):
    use_in_migrations = True

    def get_queryset(self):
        return super().get_queryset()


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Can uncomment below line for future uses (eg: searching based on a deleted data)
    # deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class BaseModelMixin(TimestampMixin):
    meta = models.JSONField(default=dict, blank=True, null=True)
    objects = BaseManager()

    class Meta:
        abstract = True

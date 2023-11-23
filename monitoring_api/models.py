from django.db import models

from core.models import BaseModelMixin


class StoreStatus(models.TextChoices):
    INACTIVE = "inactive"
    ACTIVE = "active"


class Store(BaseModelMixin):
    id = models.CharField(max_length=50, primary_key=True)
    timezone_str = models.CharField(max_length=50)

    def __str__(self):
        return self.store_id


class StoreStatusLog(BaseModelMixin):
    store_id = models.CharField(max_length=50, null=False)
    status = models.CharField(choices=StoreStatus.choices, null=False, max_length=50)
    timestamp = models.DateTimeField(verbose_name="Time Stamp in UTC", null=False)

    def __str__(self):
        return f"{self.store.store_id} - {self.status} - {self.timestamp}"


class BusinessHours(BaseModelMixin):
    store_id = models.IntegerField()
    day_of_week = models.IntegerField()
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()


class ReportStatus(models.TextChoices):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Report(BaseModelMixin):
    id = models.CharField(primary_key=True, max_length=50)
    status = models.CharField(choices=ReportStatus.choices, null=False, max_length=50)

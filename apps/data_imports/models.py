import uuid

from django.conf import settings
from django.db import models


class ImportStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    RUNNING = 'RUNNING', 'Running'
    SUCCESS = 'SUCCESS', 'Success'
    PARTIAL = 'PARTIAL', 'Partial'
    FAILED = 'FAILED', 'Failed'


class IssueSeverity(models.TextChoices):
    WARNING = 'WARNING', 'Warning'
    ERROR = 'ERROR', 'Error'


class ImportJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_file = models.CharField(max_length=255)
    source_hash = models.CharField(max_length=128, blank=True)
    source_path = models.CharField(max_length=500, blank=True)
    dry_run = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=ImportStatus.choices, default=ImportStatus.PENDING)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    initiated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    total_inserted = models.PositiveIntegerField(default=0)
    total_updated = models.PositiveIntegerField(default=0)
    total_skipped = models.PositiveIntegerField(default=0)
    total_errors = models.PositiveIntegerField(default=0)
    total_warnings = models.PositiveIntegerField(default=0)

    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-started_at']


class ImportSheetResult(models.Model):
    import_job = models.ForeignKey(ImportJob, on_delete=models.CASCADE, related_name='sheet_results')
    sheet_name = models.CharField(max_length=120)
    status = models.CharField(max_length=20, choices=ImportStatus.choices, default=ImportStatus.PENDING)
    rows_read = models.PositiveIntegerField(default=0)
    inserted = models.PositiveIntegerField(default=0)
    updated = models.PositiveIntegerField(default=0)
    skipped = models.PositiveIntegerField(default=0)
    errors = models.PositiveIntegerField(default=0)
    warnings = models.PositiveIntegerField(default=0)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sheet_name']


class ImportIssue(models.Model):
    import_job = models.ForeignKey(ImportJob, on_delete=models.CASCADE, related_name='issues')
    sheet_result = models.ForeignKey(ImportSheetResult, null=True, blank=True, on_delete=models.SET_NULL, related_name='issues')
    severity = models.CharField(max_length=10, choices=IssueSeverity.choices)
    sheet_name = models.CharField(max_length=120)
    row_number = models.PositiveIntegerField(null=True, blank=True)
    column_name = models.CharField(max_length=120, blank=True)
    error_code = models.CharField(max_length=80, blank=True)
    message = models.TextField()
    raw_value = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


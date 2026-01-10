"""Cleanup Devices Command - Keep only the latest device per user."""

from django.core.management.base import BaseCommand
from django.db.models import Count

from neural.users.models import User


class Command(BaseCommand):
    help = "Remove duplicate devices, keeping only the latest one per user"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )

    def handle(self, *args, **options):
        """Handle command usage."""
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made"))

        # Find users with more than one device
        users_with_multiple = User.objects.annotate(
            device_count=Count("devices")
        ).filter(device_count__gt=1)

        total_deleted = 0

        for user in users_with_multiple:
            # Get all devices for this user, ordered by creation date (newest first)
            devices = user.devices.order_by("-created_at")
            latest_device = devices.first()
            devices_to_delete = devices.exclude(pk=latest_device.pk)
            count = devices_to_delete.count()

            self.stdout.write(
                f"{user.email}: {devices.count()} devices -> keeping {latest_device.device_id[:20]}..."
            )

            if not dry_run:
                devices_to_delete.delete()

            total_deleted += count

        if total_deleted == 0:
            self.stdout.write(self.style.SUCCESS("No duplicate devices found"))
        else:
            action = "Would delete" if dry_run else "Deleted"
            self.stdout.write(
                self.style.SUCCESS(f"{action} {total_deleted} duplicate devices")
            )

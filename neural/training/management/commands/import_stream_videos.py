"""Import this panel's Cloudflare Stream videos.

The Cloudflare account is shared with other products, so by default this only
imports what the panel itself uploaded --videos tagged with the `neural-manager`
creator. Without that filter the gym's library would fill up with another
platform's content.

Idempotent: matching is by `stream_uid`, so running it twice updates rather
than duplicating.
"""

from django.core.management.base import BaseCommand

from neural.services import cloudflare_stream
from neural.training.models import Video


class Command(BaseCommand):
    help = "Imports videos already hosted on Cloudflare Stream."

    def add_arguments(self, parser):
        parser.add_argument(
            "--publish",
            action="store_true",
            help="Mark imported videos as published (default: drafts).",
        )
        parser.add_argument(
            "--creator",
            default=cloudflare_stream.CREATOR,
            help=(
                "Only import videos tagged with this creator. Pass an empty "
                "string to import everything in the account --including other "
                "products' videos."
            ),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be imported without writing anything.",
        )

    def handle(self, *args, **options):
        if not cloudflare_stream.is_configured():
            self.stderr.write(
                self.style.ERROR(
                    "CLOUDFLARE_STREAM_TOKEN is not set, so there is nothing to "
                    "import from."
                )
            )
            return

        creator = options["creator"] or None
        remote = cloudflare_stream.list_videos(creator=creator)
        if not remote:
            self.stdout.write(
                f"Stream returned no videos for creator {creator!r}."
                if creator
                else "Stream returned no videos."
            )
            return

        if not creator:
            self.stdout.write(
                self.style.WARNING(
                    "Importing with no creator filter: this account hosts other "
                    "products, so their videos will come in too."
                )
            )

        created = updated = 0
        for item in remote:
            uid = item.get("uid")
            if not uid:
                continue

            meta = item.get("meta") or {}
            # Stream keeps the original filename in meta.name; without it the
            # panel would show a bare uid, which tells nobody anything.
            name = meta.get("name") or meta.get("filename") or uid
            duration = item.get("duration") or 0
            ready = (item.get("status") or {}).get("state") == "ready"

            if options["dry_run"]:
                self.stdout.write(f"  would import {name} ({uid})")
                continue

            video, was_created = Video.objects.update_or_create(
                stream_uid=uid,
                defaults={
                    "name": name.rsplit(".", 1)[0],
                    "source": Video.Source.STREAM,
                    "duration_seconds": int(duration) if duration > 0 else 0,
                    "stream_ready": ready,
                    "is_published": options["publish"],
                },
            )
            created += was_created
            updated += not was_created
            self.stdout.write(
                f"  {'created' if was_created else 'updated'} {video.name} "
                f"({video.duration_seconds}s)"
            )

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING(f"\n{len(remote)} videos found, nothing written."))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\n{created} created, {updated} updated.")
            )

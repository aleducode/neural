"""Admin configuration for community app."""

from django.contrib import admin
from neural.community.models import Post, Reaction, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin for Post model."""

    list_display = [
        "id",
        "author",
        "post_type",
        "reactions_count",
        "comments_count",
        "is_active",
        "created",
    ]
    list_filter = ["post_type", "is_active", "created"]
    search_fields = ["author__email", "author__first_name", "content"]
    readonly_fields = ["reactions_count", "comments_count", "created", "modified"]
    raw_id_fields = ["author", "training"]
    ordering = ["-created"]


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    """Admin for Reaction model."""

    list_display = ["id", "user", "post", "reaction_type", "created"]
    list_filter = ["reaction_type", "created"]
    search_fields = ["user__email", "user__first_name"]
    raw_id_fields = ["user", "post"]
    ordering = ["-created"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin for Comment model."""

    list_display = ["id", "author", "post", "content_preview", "is_active", "created"]
    list_filter = ["is_active", "created"]
    search_fields = ["author__email", "author__first_name", "content"]
    raw_id_fields = ["author", "post"]
    readonly_fields = ["created", "modified"]
    ordering = ["-created"]

    @admin.display(description="Contenido")
    def content_preview(self, obj):
        """Return first 50 characters of content."""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

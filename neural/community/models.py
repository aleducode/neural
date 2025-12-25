"""Community models for posts, reactions, and comments."""

from django.db import models
from django.utils import timezone
from datetime import timedelta

from neural.users.models import User
from neural.training.models import UserTraining
from neural.utils.models import NeuralBaseModel


class Post(NeuralBaseModel):
    """Post model for community feed."""

    class PostType(models.TextChoices):
        TEXT = "text", "Solo texto"
        PHOTO = "photo", "Con foto"
        TRAINING = "training", "Entrenamiento"

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    post_type = models.CharField(
        max_length=20,
        choices=PostType.choices,
        default=PostType.TEXT,
    )
    content = models.TextField(max_length=500, blank=True)
    image = models.ImageField(
        upload_to="community/posts/",
        null=True,
        blank=True,
    )
    training = models.ForeignKey(
        UserTraining,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )

    # Denormalized counters for performance
    reactions_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Publicación"
        verbose_name_plural = "Publicaciones"
        ordering = ["-created"]

    def __str__(self):
        return f"{self.author.get_full_name()} - {self.post_type} - {self.created}"

    @property
    def time_ago(self):
        """Return human-readable time since creation."""
        now = timezone.now()
        diff = now - self.created

        if diff < timedelta(minutes=1):
            return "ahora mismo"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"hace {minutes} min"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"hace {hours}h"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"hace {days}d"
        elif diff < timedelta(days=30):
            weeks = diff.days // 7
            return f"hace {weeks}sem"
        else:
            return self.created.strftime("%d/%m/%Y")

    def update_reaction_count(self):
        """Update the reactions_count field."""
        self.reactions_count = self.reactions.count()
        self.save(update_fields=["reactions_count", "modified"])

    def update_comment_count(self):
        """Update the comments_count field."""
        self.comments_count = self.comments.filter(is_active=True).count()
        self.save(update_fields=["comments_count", "modified"])


class Reaction(NeuralBaseModel):
    """Reaction model for posts."""

    class ReactionType(models.TextChoices):
        FIRE = "fire", "Fuego"
        MUSCLE = "muscle", "Fuerza"
        CLAP = "clap", "Aplausos"
        HEART = "heart", "Me encanta"

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="reactions",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reactions",
    )
    reaction_type = models.CharField(
        max_length=20,
        choices=ReactionType.choices,
    )

    class Meta:
        verbose_name = "Reacción"
        verbose_name_plural = "Reacciones"
        # One reaction per user per post
        unique_together = ["post", "user"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.reaction_type} on {self.post.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.post.update_reaction_count()

    def delete(self, *args, **kwargs):
        post = self.post
        super().delete(*args, **kwargs)
        post.update_reaction_count()


class Comment(NeuralBaseModel):
    """Comment model for posts."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField(max_length=300)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ["created"]

    def __str__(self):
        return f"{self.author.get_full_name()} on {self.post.id}"

    @property
    def time_ago(self):
        """Return human-readable time since creation."""
        now = timezone.now()
        diff = now - self.created

        if diff < timedelta(minutes=1):
            return "ahora mismo"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"hace {minutes} min"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"hace {hours}h"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"hace {days}d"
        else:
            return self.created.strftime("%d/%m/%Y")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.post.update_comment_count()

    def delete(self, *args, **kwargs):
        post = self.post
        super().delete(*args, **kwargs)
        post.update_comment_count()

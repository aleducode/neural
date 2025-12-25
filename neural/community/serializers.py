"""Serializers for community app."""

from rest_framework import serializers
from django.db.models import Count

from neural.community.models import Post, Reaction, Comment


class PostAuthorSerializer(serializers.Serializer):
    """Serializer for post/comment author."""

    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    initials = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.get_full_name() or obj.email.split("@")[0]

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None

    def get_initials(self, obj):
        name = obj.get_full_name()
        if name:
            parts = name.split()
            if len(parts) >= 2:
                return f"{parts[0][0]}{parts[1][0]}".upper()
            return name[0:2].upper()
        return obj.email[0:2].upper()


class PostTrainingSerializer(serializers.Serializer):
    """Serializer for training attached to a post."""

    id = serializers.IntegerField(source="slot.id")
    type = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()

    def get_type(self, obj):
        if obj.slot and obj.slot.class_training:
            return obj.slot.class_training.training_type.name
        return "Entrenamiento"

    def get_date(self, obj):
        if obj.slot:
            return obj.slot.date.strftime("%Y-%m-%d")
        return None

    def get_duration_minutes(self, obj):
        if obj.slot and obj.slot.class_training:
            start = obj.slot.class_training.hour_init
            end = obj.slot.class_training.hour_end
            from datetime import datetime

            start_dt = datetime.combine(datetime.today(), start)
            end_dt = datetime.combine(datetime.today(), end)
            diff = end_dt - start_dt
            return int(diff.total_seconds() / 60)
        return 60  # Default


class ReactionsSummarySerializer(serializers.Serializer):
    """Serializer for reactions summary."""

    fire = serializers.IntegerField(default=0)
    muscle = serializers.IntegerField(default=0)
    clap = serializers.IntegerField(default=0)
    heart = serializers.IntegerField(default=0)


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post model."""

    author = PostAuthorSerializer(read_only=True)
    training = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()
    reactions_summary = serializers.SerializerMethodField()
    time_ago = serializers.CharField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "post_type",
            "content",
            "image_url",
            "training",
            "reactions_count",
            "comments_count",
            "user_reaction",
            "reactions_summary",
            "time_ago",
            "created",
        ]
        read_only_fields = [
            "id",
            "author",
            "reactions_count",
            "comments_count",
            "time_ago",
            "created",
        ]

    def get_training(self, obj):
        if obj.training:
            return PostTrainingSerializer(obj.training, context=self.context).data
        return None

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_user_reaction(self, obj):
        """Get current user's reaction on this post."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            reaction = obj.reactions.filter(user=request.user).first()
            if reaction:
                return reaction.reaction_type
        return None

    def get_reactions_summary(self, obj):
        """Get count of each reaction type."""
        summary = {"fire": 0, "muscle": 0, "clap": 0, "heart": 0}
        reactions = (
            obj.reactions.values("reaction_type")
            .annotate(count=Count("id"))
            .order_by()
        )
        for r in reactions:
            if r["reaction_type"] in summary:
                summary[r["reaction_type"]] = r["count"]
        return summary


class CreatePostSerializer(serializers.ModelSerializer):
    """Serializer for creating a post."""

    training_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = ["content", "image", "training_id"]

    def create(self, validated_data):
        training_id = validated_data.pop("training_id", None)
        user = self.context["request"].user

        # Determine post type
        if validated_data.get("image"):
            post_type = Post.PostType.PHOTO
        elif training_id:
            post_type = Post.PostType.TRAINING
        else:
            post_type = Post.PostType.TEXT

        # Get training if provided
        training = None
        if training_id:
            from neural.training.models import UserTraining

            training = UserTraining.objects.filter(
                id=training_id,
                user=user,
            ).first()

        post = Post.objects.create(
            author=user,
            post_type=post_type,
            training=training,
            **validated_data,
        )
        return post


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model."""

    author = PostAuthorSerializer(read_only=True)
    time_ago = serializers.CharField(read_only=True)
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "author",
            "content",
            "time_ago",
            "created",
            "is_mine",
        ]
        read_only_fields = ["id", "author", "time_ago", "created", "is_mine"]

    def get_is_mine(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.author_id == request.user.id
        return False


class CreateCommentSerializer(serializers.ModelSerializer):
    """Serializer for creating a comment."""

    class Meta:
        model = Comment
        fields = ["content"]


class ReactionSerializer(serializers.Serializer):
    """Serializer for adding a reaction."""

    reaction_type = serializers.ChoiceField(
        choices=Reaction.ReactionType.choices,
    )

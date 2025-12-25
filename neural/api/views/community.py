"""API views for community feature."""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from neural.community.models import Post, Reaction, Comment
from neural.community.serializers import (
    PostSerializer,
    CreatePostSerializer,
    CommentSerializer,
    CreateCommentSerializer,
    ReactionSerializer,
)


class FeedView(APIView):
    """Get community feed with pagination."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        page_size = 20
        offset = (page - 1) * page_size

        posts = (
            Post.objects.filter(is_active=True)
            .select_related("author", "training", "training__slot")
            .prefetch_related("reactions")
            .order_by("-created")[offset : offset + page_size + 1]
        )

        # Check if there are more posts
        has_more = len(posts) > page_size
        posts = posts[:page_size]

        serializer = PostSerializer(
            posts,
            many=True,
            context={"request": request},
        )

        return Response(
            {
                "posts": serializer.data,
                "next_page": page + 1 if has_more else None,
                "has_more": has_more,
            }
        )


class PostListCreateView(APIView):
    """Create a post or list posts."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = CreatePostSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            post = serializer.save()
            return Response(
                PostSerializer(post, context={"request": request}).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    """Get, update or delete a post."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        post = get_object_or_404(
            Post.objects.select_related("author", "training", "training__slot")
            .prefetch_related("reactions"),
            pk=pk,
            is_active=True,
        )
        serializer = PostSerializer(post, context={"request": request})
        return Response({"post": serializer.data})

    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk, author=request.user, is_active=True)
        post.is_active = False
        post.save(update_fields=["is_active", "modified"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostReactionView(APIView):
    """Add or remove reaction from a post."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """Add or change reaction."""
        post = get_object_or_404(Post, pk=pk, is_active=True)
        serializer = ReactionSerializer(data=request.data)

        if serializer.is_valid():
            reaction_type = serializer.validated_data["reaction_type"]

            # Update or create reaction
            reaction, created = Reaction.objects.update_or_create(
                post=post,
                user=request.user,
                defaults={"reaction_type": reaction_type},
            )

            # Get updated summary
            from django.db.models import Count

            summary = {"fire": 0, "muscle": 0, "clap": 0, "heart": 0}
            reactions = (
                post.reactions.values("reaction_type")
                .annotate(count=Count("id"))
                .order_by()
            )
            for r in reactions:
                if r["reaction_type"] in summary:
                    summary[r["reaction_type"]] = r["count"]

            return Response(
                {
                    "success": True,
                    "reactions_count": post.reactions_count,
                    "reactions_summary": summary,
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Remove reaction."""
        post = get_object_or_404(Post, pk=pk, is_active=True)
        Reaction.objects.filter(post=post, user=request.user).delete()

        # Get updated summary
        from django.db.models import Count

        summary = {"fire": 0, "muscle": 0, "clap": 0, "heart": 0}
        reactions = (
            post.reactions.values("reaction_type")
            .annotate(count=Count("id"))
            .order_by()
        )
        for r in reactions:
            if r["reaction_type"] in summary:
                summary[r["reaction_type"]] = r["count"]

        return Response(
            {
                "success": True,
                "reactions_count": post.reactions_count,
                "reactions_summary": summary,
            }
        )


class PostCommentsView(APIView):
    """Get or add comments to a post."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Get all comments for a post."""
        post = get_object_or_404(Post, pk=pk, is_active=True)
        comments = post.comments.filter(is_active=True).select_related("author")
        serializer = CommentSerializer(
            comments,
            many=True,
            context={"request": request},
        )
        return Response({"comments": serializer.data})

    def post(self, request, pk):
        """Add a comment to a post."""
        post = get_object_or_404(Post, pk=pk, is_active=True)
        serializer = CreateCommentSerializer(data=request.data)

        if serializer.is_valid():
            comment = Comment.objects.create(
                post=post,
                author=request.user,
                **serializer.validated_data,
            )
            return Response(
                CommentSerializer(comment, context={"request": request}).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    """Delete a comment."""

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        """Delete a comment (only author can delete)."""
        comment = get_object_or_404(
            Comment,
            pk=pk,
            author=request.user,
            is_active=True,
        )
        comment.is_active = False
        comment.save(update_fields=["is_active", "modified"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserTrainingsForPostView(APIView):
    """Get user's recent trainings for sharing in posts."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get last 5 completed trainings."""
        from neural.training.models import UserTraining
        from django.utils import timezone
        from datetime import timedelta

        # Get trainings from last 30 days
        thirty_days_ago = timezone.localdate() - timedelta(days=30)

        trainings = (
            UserTraining.objects.filter(
                user=request.user,
                status__in=[UserTraining.Status.CONFIRMED, UserTraining.Status.DONE],
                slot__date__gte=thirty_days_ago,
            )
            .select_related("slot", "slot__class_training", "slot__class_training__training_type")
            .order_by("-slot__date")[:5]
        )

        data = []
        for t in trainings:
            if t.slot and t.slot.class_training:
                training_type = t.slot.class_training.training_type.name
                hour_init = t.slot.class_training.hour_init
                hour_end = t.slot.class_training.hour_end

                from datetime import datetime

                start_dt = datetime.combine(datetime.today(), hour_init)
                end_dt = datetime.combine(datetime.today(), hour_end)
                duration = int((end_dt - start_dt).total_seconds() / 60)

                data.append(
                    {
                        "id": t.id,
                        "type": training_type,
                        "date": t.slot.date.strftime("%Y-%m-%d"),
                        "duration_minutes": duration,
                    }
                )

        return Response({"trainings": data})

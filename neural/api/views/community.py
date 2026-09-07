"""API views for community feature."""

import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.utils import timezone

from neural.community.models import Post, Reaction, Comment
from neural.users.models import User, Profile, UserStrike
from neural.community.serializers import (
    PostSerializer,
    CreatePostSerializer,
    CommentSerializer,
    CreateCommentSerializer,
    ReactionSerializer,
)
from neural.services.push_notifications import (
    PushNotificationService,
    NotificationPayload,
)
from neural.users.models import PushNotification
from neural.users.tasks import send_community_notification_to_all

logger = logging.getLogger(__name__)

# Emoji mapping for reactions
REACTION_EMOJIS = {
    "fire": "🔥",
    "muscle": "💪",
    "clap": "👏",
    "heart": "❤️",
}


def display_name(user):
    """Nombre del socio, o None si nunca lo cargo.

    Antes caia al prefijo del correo, que publicaba media direccion ajena en
    la pantalla de otro socio. La app pinta las iniciales cuando viene vacio.
    """
    return user.get_full_name().strip() or None


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

            # Send push notification to all users (except the author) - async via Celery
            try:
                user_name = (
                    request.user.get_full_name() or request.user.email.split("@")[0]
                )

                # Determine notification body based on post type
                if post.post_type == Post.PostType.TRAINING:
                    body = f"{user_name} compartió un entrenamiento"
                elif post.post_type == Post.PostType.PHOTO:
                    body = f"{user_name} compartió una foto"
                else:
                    content_preview = (
                        post.content[:50] + "..."
                        if len(post.content) > 50
                        else post.content
                    )
                    body = f"{user_name}: {content_preview}"

                # Send asynchronously via Celery task
                send_community_notification_to_all.delay(
                    title="📢 Nueva publicación",
                    body=body,
                    data={
                        "type": "community_new_post",
                        "post_id": post.id,
                    },
                    exclude_user_ids=[request.user.id],
                )
            except Exception as e:
                logger.error(f"Error queuing new post notification: {e}")

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
            Post.objects.select_related(
                "author", "training", "training__slot"
            ).prefetch_related("reactions"),
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

            # Send push notification to post author (only for new reactions, not self-reactions)
            if created and post.author_id != request.user.id:
                try:
                    emoji = REACTION_EMOJIS.get(reaction_type, "👍")
                    user_name = (
                        request.user.get_full_name() or request.user.email.split("@")[0]
                    )

                    payload = NotificationPayload(
                        title=f"{emoji} Nueva reacción",
                        body=f"{user_name} reaccionó a tu publicación",
                        notification_type=PushNotification.NotificationType.COMMUNITY,
                        data={
                            "type": "community_reaction",
                            "post_id": post.id,
                            "reaction_type": reaction_type,
                        },
                    )
                    PushNotificationService.send_to_user(post.author, payload)
                except Exception as e:
                    logger.error(f"Error sending reaction notification: {e}")

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

            # Send push notification to post author (not for self-comments)
            if post.author_id != request.user.id:
                try:
                    user_name = (
                        request.user.get_full_name() or request.user.email.split("@")[0]
                    )
                    comment_preview = (
                        comment.content[:50] + "..."
                        if len(comment.content) > 50
                        else comment.content
                    )

                    payload = NotificationPayload(
                        title="💬 Nuevo comentario",
                        body=f"{user_name}: {comment_preview}",
                        notification_type=PushNotification.NotificationType.COMMUNITY,
                        data={
                            "type": "community_comment",
                            "post_id": post.id,
                            "comment_id": comment.id,
                        },
                    )
                    PushNotificationService.send_to_user(post.author, payload)
                except Exception as e:
                    logger.error(f"Error sending comment notification: {e}")

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
            .select_related(
                "slot", "slot__class_training", "slot__class_training__training_type"
            )
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


class UserPublicProfileView(APIView):
    """Get public profile of a user for community view."""

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        """Get user's public profile with stats."""
        from neural.training.models import UserTraining

        user = get_object_or_404(User, pk=user_id)

        # Get profile
        profile = Profile.objects.filter(user=user).first()

        # Get current strike
        current_strike = UserStrike.objects.filter(user=user, is_current=True).first()

        # Get total trainings count
        total_trainings = UserTraining.objects.filter(
            user=user,
            status__in=[UserTraining.Status.CONFIRMED, UserTraining.Status.DONE],
        ).count()

        # Get user's posts count
        posts_count = Post.objects.filter(author=user, is_active=True).count()

        # Get user's recent posts (last 5)
        recent_posts = (
            Post.objects.filter(author=user, is_active=True)
            .select_related("training", "training__slot")
            .prefetch_related("reactions")
            .order_by("-created")[:5]
        )

        # Build photo URL
        photo_url = None
        if user.photo:
            photo_url = request.build_absolute_uri(user.photo.url)
        elif profile and profile.photo:
            photo_url = request.build_absolute_uri(profile.photo.url)

        # Build response
        data = {
            "id": user.id,
            "name": display_name(user),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "photo_url": photo_url,
            "instagram": profile.instagram if profile else None,
            "profession": profile.profession if profile else None,
            "member_since": user.created.strftime("%B %Y") if user.created else None,
            "stats": {
                "total_trainings": total_trainings,
                "current_strike": current_strike.weeks if current_strike else 0,
                "posts_count": posts_count,
            },
            "recent_posts": PostSerializer(
                recent_posts, many=True, context={"request": request}
            ).data,
        }

        return Response(data)


class LeaderboardView(APIView):
    """Ranking de la comunidad por entrenamientos, racha o publicaciones."""

    permission_classes = [IsAuthenticated]

    METRICS = ("trainings", "strike", "posts")
    PERIODS = ("week", "month", "all")
    MAX_ENTRIES = 100

    def _period_range(self, period):
        """Rango de fechas del periodo.

        La semana es la ISO (lunes a domingo), la misma que usan UserStats y
        UserStrike, para que el ranking no contradiga a la racha.
        """
        from datetime import timedelta

        today = timezone.localdate()
        if period == "week":
            start = today - timedelta(days=today.weekday())
            return start, start + timedelta(days=6)
        if period == "month":
            start = today.replace(day=1)
            next_month = (start + timedelta(days=32)).replace(day=1)
            return start, next_month - timedelta(days=1)
        return None, None

    def _annotate(self, users, metric, start, end):
        from django.db.models import Count, Max, Q
        from django.db.models.functions import Coalesce

        from neural.training.models import UserTraining

        if metric == "strike":
            # La racha es un acumulado propio: el periodo no aplica.
            return users.annotate(
                value=Coalesce(
                    Max("strikes__weeks", filter=Q(strikes__is_current=True)), 0
                )
            )

        if metric == "posts":
            condition = Q(posts__is_active=True)
            if start:
                condition &= Q(posts__created__date__gte=start, posts__created__date__lte=end)
            return users.annotate(value=Count("posts", filter=condition, distinct=True))

        condition = Q(trainings__status=UserTraining.Status.CONFIRMED)
        if start:
            condition &= Q(trainings__slot__date__gte=start, trainings__slot__date__lte=end)
        return users.annotate(value=Count("trainings", filter=condition, distinct=True))

    def _photo_url(self, request, user):
        if user.photo:
            return request.build_absolute_uri(user.photo.url)
        profile = getattr(user, "profile", None)
        if profile and profile.photo:
            return request.build_absolute_uri(profile.photo.url)
        return None

    def _initials(self, user):
        name = user.get_full_name().strip()
        parts = name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        if name:
            return name[:2].upper()
        return user.email[:2].upper()

    def get(self, request):
        metric = request.query_params.get("metric", "trainings")
        period = request.query_params.get("period", "week")
        if metric not in self.METRICS:
            metric = "trainings"
        if period not in self.PERIODS:
            period = "week"

        try:
            limit = min(int(request.query_params.get("limit", 25)), self.MAX_ENTRIES)
        except (TypeError, ValueError):
            limit = 25
        limit = max(limit, 1)

        start, end = self._period_range(period)

        # is_client no alcanza para separar socios: las cuentas internas
        # (neuralconsciente@gmail.com y otras dos) lo tienen en True y se
        # colaban de primeras en el ranking.
        users = (
            User.objects.filter(
                is_active=True, is_verified=True, is_client=True, is_staff=False
            )
            # exclude() y no filter(): quien no tiene Profile sigue entrando.
            .exclude(profile__hide_from_leaderboard=True)
            .select_related("profile")
        )
        users = self._annotate(users, metric, start, end)

        # Desempate estable por nombre para que no salte entre refrescos.
        ranked = list(users.order_by("-value", "first_name", "last_name", "id"))

        # Posiciones unicas y consecutivas: dos socios con el mismo valor
        # quedan en puestos distintos, separados por el desempate de arriba.
        values = [u.value for u in ranked]

        entries = []
        for index, user in enumerate(ranked[:limit]):
            entries.append(
                {
                    "position": index + 1,
                    "user_id": user.id,
                    "name": display_name(user),
                    "photo_url": self._photo_url(request, user),
                    "initials": self._initials(user),
                    "value": user.value,
                }
            )

        me = None
        for index, user in enumerate(ranked):
            if user.id != request.user.id:
                continue
            above = ranked[index - 1] if index else None
            me = {
                "position": index + 1,
                "value": user.value,
                # Diferencia con quien esta justo arriba, para que concuerde
                # con la posicion. Puede ser 0: mismo valor, y solo los separa
                # el desempate por nombre.
                "to_next": (above.value - user.value) if above else None,
                # Quien esta justo arriba. Sale de `ranked`, que ya excluye a
                # quienes se ocultaron del ranking, asi que no puede filtrar a
                # alguien que pidio no aparecer.
                "next_up": (
                    {
                        "name": display_name(above),
                        "value": above.value,
                    }
                    if above
                    else None
                ),
            }
            break

        return Response(
            {
                "period": {
                    "start": start.isoformat() if start else None,
                    "end": end.isoformat() if end else None,
                },
                "metric": metric,
                "me": me,
                "entries": entries,
                "total": len(ranked),
            }
        )

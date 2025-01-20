from django.conf import settings
from django.core.cache import cache
from django.utils import timezone


def settings_context(_request):
    """Settings available by default to the templates context."""
    # Note: we intentionally do NOT expose the entire settings
    # to prevent accidental leaking of sensitive information
    return {
        "DEBUG": settings.DEBUG,
        "BOLD_KEY": settings.BOLD_KEY,
        "BOLD_SECRET": settings.BOLD_SECRET,
    }


def user_membership(request):
    user = request.user
    if not user.is_authenticated:
        return {"membership": None}

    # Calculate the end of the current day in the server's timezone
    now = timezone.now()
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    seconds_until_midnight = (end_of_day - now).total_seconds()

    # Create a unique cache key for each user and day
    cache_key = f"user_membership_{user.id}_{now.date()}"

    # Try to get the cached membership
    membership = cache.get(cache_key)

    if membership is None:
        # If not in cache, query the database
        membership = user.memberships.filter(is_active=True).first()

        # Cache until end of day
        cache.set(cache_key, membership, timeout=int(seconds_until_midnight))

    return {"membership": membership}

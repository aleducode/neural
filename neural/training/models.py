"""User model."""

from slugify import slugify

# Django
from django.utils import timezone
import math
import re
from django.db import models
from django.db.models import Q

from neural.users.models import User

# Utils
from neural.utils.models import NeuralBaseModel


class Space(NeuralBaseModel):
    slug_name = models.SlugField(max_length=50)
    name = models.CharField(max_length=255)
    description = models.CharField(null=True, blank=True, max_length=255)

    def save(self, *args, **kwargs):
        self.slug_name = slugify(self.name, separator="_").lower()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}-{self.description}"


class TrainingType(NeuralBaseModel):
    """Traingin type model."""

    name = models.CharField(max_length=255)
    slug_name = models.SlugField(unique=True, max_length=100)
    is_group = models.BooleanField(default=True)
    photo = models.ImageField(
        "Foto de la clase",
        upload_to="training_types/",
        blank=True,
        null=True,
        help_text="Se ve en el panel, en «Clases más pedidas». 320x352 o mayor.",
    )

    def __str__(self):
        """Return training type."""
        return self.name

    class Meta:
        """Meta class."""

        verbose_name = "Tipo de entrenamiento"
        verbose_name_plural = "Tipos de entrenamientos"

    def save(self, *args, **kwargs):
        if not self.slug_name:
            self.slug_name = slugify(self.name, separator="-")
        super().save(*args, **kwargs)


class Classes(NeuralBaseModel):
    """Classes model."""

    class DaysChoices(models.TextChoices):
        MONDAY = "MONDAY", "Lunes"
        TUESDAY = "TUESDAY", "Martes"
        WEDNESDAY = "WEDNESDAY", "Miércoles"
        THURSDAY = "THURSDAY", "Jueves"
        FRIDAY = "FRIDAY", "Viernes"
        SATURDAY = "SATURDAY", "Sábado"
        SUNDAY = "SUNDAY", "Domingo"

    day = models.CharField(
        max_length=10, choices=DaysChoices.choices, default=DaysChoices.MONDAY
    )
    training_type = models.ForeignKey(
        TrainingType, on_delete=models.CASCADE, related_name="classes"
    )
    hour_init = models.TimeField()
    hour_end = models.TimeField()

    def __str__(self):
        """Return training type."""
        return f"{self.training_type} - {self.day}"

    class Meta:
        """Meta class."""

        verbose_name = "Calendario de clases"
        verbose_name_plural = "Calendario de clases"
        constraints = [
            models.UniqueConstraint(
                fields=["day", "hour_init", "hour_end", "training_type"],
                name="unique_class_combination",
            )
        ]


class Slot(NeuralBaseModel):
    date = models.DateField()
    max_places = models.IntegerField()
    class_training = models.ForeignKey(
        Classes, on_delete=models.CASCADE, related_name="slots", blank=True, null=True
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Clase {self.date} - {self.class_training.hour_init} - {self.class_training.hour_end}"

    @property
    def users_scheduled(self):
        return self.user_trainings.filter(status="CONFIRMED")

    @property
    def available_places(self):
        return self.max_places - self.users_scheduled.count()

    @property
    def users(self):
        return self.users_scheduled.all().select_related("user")


class UserTraining(NeuralBaseModel):
    """Gym session model."""

    class Status(models.TextChoices):
        CANCELLED = "CANCELLED", "Cancelada"
        CONFIRMED = "CONFIRMED", "Confirmada"
        DONE = "DONE", "Terminada"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="trainings",
        limit_choices_to={"is_verified": True},
    )
    slot = models.ForeignKey(
        Slot, on_delete=models.CASCADE, related_name="user_trainings"
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )
    space = models.ForeignKey(
        Space,
        on_delete=models.CASCADE,
        related_name="user_trainings",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Entrenamiento: {self.user.get_full_name()} - {self.user}"

    @property
    def is_now(self):
        return self.slot.date == timezone.localdate()


class Video(NeuralBaseModel):
    """A training video.

    The source is either a URL (YouTube, Vimeo) or an uploaded file. Which one is
    stored explicitly rather than guessed from the field contents, and `playback`
    hands out the address without the rest of the code having to know which."""

    class Source(models.TextChoices):
        URL = "url", "Enlace"
        STREAM = "stream", "Cloudflare Stream"
        UPLOAD = "upload", "Archivo subido"

    class Level(models.TextChoices):
        ALL = "all", "Todos los niveles"
        BEGINNER = "beginner", "Principiante"
        INTERMEDIATE = "intermediate", "Intermedio"
        ADVANCED = "advanced", "Avanzado"

    name = models.CharField("Nombre", max_length=255)
    description = models.TextField("Descripción", blank=True, default="")
    source = models.CharField(
        "Fuente", max_length=10, choices=Source.choices, default=Source.URL
    )
    url = models.URLField("Enlace", max_length=500, blank=True, default="")
    file = models.FileField(
        "Archivo", upload_to="videos/", blank=True, null=True
    )
    stream_uid = models.CharField(
        "UID en Cloudflare Stream", max_length=64, blank=True, default="", db_index=True
    )
    stream_ready = models.BooleanField("Listo en Stream", default=False)
    thumbnail = models.ImageField(
        "Miniatura", upload_to="videos/thumbs/", blank=True, null=True
    )
    duration_seconds = models.PositiveIntegerField("Duración (s)", default=0)
    poster_second = models.PositiveIntegerField(
        "Segundo de la miniatura",
        default=1,
        help_text=(
            "De qué momento del video sale la miniatura. En el segundo 1 "
            "casi nadie empezó todavía: elegí uno donde se vea el movimiento."
        ),
    )
    training_type = models.ForeignKey(
        TrainingType,
        on_delete=models.SET_NULL,
        related_name="videos",
        blank=True,
        null=True,
    )
    level = models.CharField(
        "Nivel", max_length=20, choices=Level.choices, default=Level.ALL
    )
    is_published = models.BooleanField("Publicado", default=False)

    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videos"
        ordering = ["-created"]

    def __str__(self):
        return self.name

    @property
    def playback(self):
        """The video's address, wherever it comes from."""
        if self.source == self.Source.STREAM and self.stream_uid:
            from neural.services import cloudflare_stream

            return cloudflare_stream.playback_url(self.stream_uid)
        if self.source == self.Source.UPLOAD and self.file:
            try:
                return self.file.url
            except ValueError:
                return None
        return self.url or None

    @property
    def embed(self):
        """The embeddable player. Stream brings its own, with HLS."""
        if self.source == self.Source.STREAM and self.stream_uid:
            from neural.services import cloudflare_stream

            return cloudflare_stream.iframe_url(self.stream_uid)
        if self.youtube_id:
            return f"https://www.youtube.com/embed/{self.youtube_id}"
        return self.playback

    @property
    def youtube_id(self):
        """The YouTube id, for the thumbnail and the embedded player."""
        if self.source != self.Source.URL or not self.url:
            return None
        match = re.search(
            r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/))([\w-]{11})",
            self.url,
        )
        return match.group(1) if match else None

    @property
    def player(self):
        """Con que reproductor se ve. La app no tiene que deducirlo de `source`:
        un enlace que no sea de YouTube es un archivo directo, y `embed` en ese
        caso es igual a `playback`, asi que no sirve para distinguirlos."""
        if self.source == self.Source.STREAM and self.stream_uid:
            return "hls"
        if self.youtube_id:
            return "youtube"
        return "file"

    @property
    def poster(self):
        """Its own thumbnail; failing that, the one the host generates."""
        if self.thumbnail:
            try:
                return self.thumbnail.url
            except ValueError:
                pass
        if self.source == self.Source.STREAM and self.stream_uid:
            from neural.services import cloudflare_stream

            # Cloudflare responde 400 si el segundo cae fuera del video, y
            # entonces la miniatura no carga en ningun lado.
            tope = max(self.duration_seconds - 1, 1) if self.duration_seconds else 1
            return cloudflare_stream.thumbnail_url(
                self.stream_uid, second=min(self.poster_second or 1, tope)
            )
        return (
            f"https://i.ytimg.com/vi/{self.youtube_id}/hqdefault.jpg"
            if self.youtube_id
            else None
        )


class VideoPackage(NeuralBaseModel):
    """A video package: an ordered list that gets assigned to someone."""

    class Kind(models.TextChoices):
        GROUP = "group", "Grupal"
        INDIVIDUAL = "individual", "Individual"

    name = models.CharField("Nombre", max_length=255)
    description = models.TextField("Descripción", blank=True, default="")
    cover = models.ImageField(
        "Portada", upload_to="packages/", blank=True, null=True
    )
    kind = models.CharField(
        "Modalidad", max_length=15, choices=Kind.choices, default=Kind.GROUP
    )
    is_published = models.BooleanField("Publicado", default=False)
    videos = models.ManyToManyField(
        Video, through="PackageVideo", related_name="packages"
    )

    class Meta:
        verbose_name = "Paquete de videos"
        verbose_name_plural = "Paquetes de videos"
        ordering = ["-created"]

    def __str__(self):
        return self.name


class PackageVideo(NeuralBaseModel):
    """One video inside a package, in its position."""

    package = models.ForeignKey(
        VideoPackage, on_delete=models.CASCADE, related_name="items"
    )
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="items")
    order = models.PositiveIntegerField("Orden", default=0)
    notes = models.CharField(
        "Notas del entrenador", max_length=500, blank=True, default=""
    )

    class Meta:
        verbose_name = "Video del paquete"
        verbose_name_plural = "Videos del paquete"
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["package", "video"], name="unique_video_per_package"
            )
        ]

    def __str__(self):
        return f"{self.package} · {self.order}. {self.video}"


class PackageAssignment(NeuralBaseModel):
    """Who a package reaches.

        Exactly one of three: a member, a whole plan, or everyone. More than one at
        a time would make it ambiguous who it was assigned to."""

    package = models.ForeignKey(
        VideoPackage, on_delete=models.CASCADE, related_name="assignments"
    )
    # Para firmar la nota en la app: "Nota de Juan" en vez de un rotulo frio.
    # Nulo en lo ya asignado, que se hizo antes de que existiera el campo.
    assigned_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="packages_assigned",
        blank=True,
        null=True,
        verbose_name="Asignado por",
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="video_packages",
        blank=True,
        null=True,
    )
    plan = models.ForeignKey(
        "users.NeuralPlan",
        on_delete=models.CASCADE,
        related_name="video_packages",
        blank=True,
        null=True,
    )
    everyone = models.BooleanField("Para todos", default=False)

    class Meta:
        verbose_name = "Asignación de paquete"
        verbose_name_plural = "Asignaciones de paquetes"
        ordering = ["-created"]
        constraints = [
            models.CheckConstraint(
                name="assignment_has_exactly_one_target",
                check=(
                    Q(user__isnull=False, plan__isnull=True, everyone=False)
                    | Q(user__isnull=True, plan__isnull=False, everyone=False)
                    | Q(user__isnull=True, plan__isnull=True, everyone=True)
                ),
            )
        ]

    def __str__(self):
        target = self.user or self.plan or "todos"
        return f"{self.package} → {target}"


class VideoProgress(NeuralBaseModel):
    """How much of a video a member watched.

        This is what turns the library into data: without it the panel knows a
        package was assigned, but not whether anyone watched it."""

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="video_progress"
    )
    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name="progress"
    )
    seconds = models.PositiveIntegerField("Segundos vistos", default=0)
    completed_at = models.DateTimeField("Completado", blank=True, null=True)

    class Meta:
        verbose_name = "Progreso de video"
        verbose_name_plural = "Progreso de videos"
        ordering = ["-modified"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "video"], name="unique_progress_per_user_video"
            )
        ]

    def __str__(self):
        return f"{self.user} · {self.video} · {self.seconds}s"

    @property
    def percent(self):
        total = self.video.duration_seconds
        return min(round((self.seconds / total) * 100), 100) if total else 0


class VideoUpload(NeuralBaseModel):
    """An upload in progress, split into chunks.

    It exists so a heavy video on bad internet can be resumed: every chunk that
    arrives is recorded, and if the connection drops the browser asks which
    ones are missing instead of starting over.

    When hosting moves to an external service (Cloudflare Stream, Mux), this is
    replaced by its direct upload URL and the file stops going through Django.
    The shape of the flow --init, send chunks, complete-- is the same, so the
    client does not change.
    """

    token = models.CharField("Token", max_length=64, unique=True, db_index=True)
    # When the upload goes straight to Cloudflare the browser sends the chunks
    # to this URL and Django only asked for it: the file never passes through.
    direct_url = models.URLField("URL de subida directa", max_length=1000, blank=True, default="")
    stream_uid = models.CharField("UID en Stream", max_length=64, blank=True, default="")
    filename = models.CharField("Nombre del archivo", max_length=255)
    size = models.PositiveBigIntegerField("Tamaño total")
    chunk_size = models.PositiveIntegerField("Tamaño del trozo")
    received = models.JSONField("Trozos recibidos", default=list)
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="uploads",
        blank=True,
        null=True,
    )
    completed_at = models.DateTimeField("Completada", blank=True, null=True)

    class Meta:
        verbose_name = "Subida de video"
        verbose_name_plural = "Subidas de video"
        ordering = ["-created"]

    def __str__(self):
        return f"{self.filename} ({len(self.received)}/{self.total_chunks})"

    @property
    def total_chunks(self):
        return math.ceil(self.size / self.chunk_size) if self.chunk_size else 0

    @property
    def is_complete(self):
        return len(set(self.received)) >= self.total_chunks > 0

    def chunk_path(self, index):
        return f"uploads/{self.token}/{index:06d}.part"

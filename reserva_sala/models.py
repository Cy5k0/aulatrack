from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    def create_user(self, email, rut, password=None, **extra_fields):
        if not email:
            raise ValueError("El Email es obligatorio")
        if not rut:
            raise ValueError("El RUT es obligatorio")

        email = self.normalize_email(email)
        user = self.model(email=email, rut=rut, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, rut, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser debe tener is_superuser=True.")

        return self.create_user(email, rut, password, **extra_fields)


class Usuario(AbstractUser):
    username = None  # Deshabilitamos el campo username predeterminado
    rut = models.CharField(max_length=12, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    ESTADOS_CHOICES = [
        ("Presente", "Presente"),
        ("Con Permiso", "Con Permiso"),
        ("Con Licencia Médica", "Con Licencia Médica"),
    ]
    estado = models.CharField(
        max_length=20, choices=ESTADOS_CHOICES, default="Presente"
    )

    # Campos requeridos por Django al extender AbstractUser
    USERNAME_FIELD = "email"  # Usamos email como campo de login en lugar de username
    REQUIRED_FIELDS = ["rut", "first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.rut})"


class Sala(models.Model):
    ESTADO_CHOICES = [
        ("Desocupada", "Desocupada"),
        ("Ocupada", "Ocupada"),
        ("Inhabilitada", "Inhabilitada"),
    ]

    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="Desocupada"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class AccesoSala(models.Model):
    BLOQUES_HORARIOS_CHOICES = [
        ("1", "Bloque 1 (8:15-9:00)"),
        ("2", "Bloque 2 (9:00-9:45)"),
        ("3", "Bloque 3 (10:15-11:00)"),
        ("4", "Bloque 4 (11:00-11:45)"),
        ("5", "Bloque 5 (12:00-12:45)"),
        ("6", "Bloque 6 (12:45-13:30)"),
        ("7", "Bloque 7 (14:15-15:00)"),
        ("8", "Bloque 8 (15:00-15:45)"),
    ]

    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="accesos"
    )
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name="accesos")
    clave_acceso = models.CharField(max_length=50)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_reserva = models.DateField()
    bloque_horario = models.CharField(
        max_length=2,
        choices=BLOQUES_HORARIOS_CHOICES,
        help_text="Seleccione el bloque horario para la reserva",
    )
    curso = models.CharField(max_length=100, blank=True, null=True, 
                            help_text="Indique el curso con el que asistirá")
    descripcion_actividad = models.TextField(blank=True, null=True,
                                           help_text="Describa brevemente la actividad a realizar")

    class Meta:
        unique_together = ("usuario", "sala", "fecha_reserva", "bloque_horario")
        ordering = ["-fecha_reserva", "bloque_horario"]

    def __str__(self):
        return f"Reserva de {self.usuario.first_name} {self.usuario.last_name} en {self.sala.nombre} - {self.fecha_reserva} ({self.get_bloque_horario_display()})"

    def clean(self):
        # Modificar para evitar el error cuando sala aún no está asignada
        if hasattr(self, 'sala') and self.sala is not None:
            # Validar que no haya reservas duplicadas
            if AccesoSala.objects.filter(
                sala=self.sala,
                fecha_reserva=self.fecha_reserva,
                bloque_horario=self.bloque_horario,
            ).exclude(id=self.id).exists():
                raise ValidationError("Este bloque ya está reservado")


# Create your models here.

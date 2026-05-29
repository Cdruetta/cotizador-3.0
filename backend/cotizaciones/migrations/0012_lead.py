from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("cotizaciones", "0011_cliente_activo"),
    ]

    operations = [
        migrations.CreateModel(
            name="Lead",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=255, verbose_name="Nombre")),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, null=True, verbose_name="Email"
                    ),
                ),
                (
                    "telefono",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="Teléfono"
                    ),
                ),
                (
                    "empresa",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Empresa"
                    ),
                ),
                (
                    "cargo",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Cargo"
                    ),
                ),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("nuevo", "Nuevo"),
                            ("contactado", "Contactado"),
                            ("calificado", "Calificado"),
                            ("propuesta", "Propuesta"),
                            ("negociacion", "Negociación"),
                            ("ganado", "Ganado"),
                            ("perdido", "Perdido"),
                        ],
                        default="nuevo",
                        max_length=20,
                        verbose_name="Estado",
                    ),
                ),
                (
                    "fuente",
                    models.CharField(
                        choices=[
                            ("web", "Web"),
                            ("referral", "Referido"),
                            ("llamada", "Llamada"),
                            ("email", "Email"),
                            ("redes_sociales", "Redes Sociales"),
                            ("whatsapp", "WhatsApp"),
                            ("otro", "Otro"),
                        ],
                        default="web",
                        max_length=20,
                        verbose_name="Fuente",
                    ),
                ),
                (
                    "notas",
                    models.TextField(blank=True, null=True, verbose_name="Notas"),
                ),
                (
                    "asignado_a",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Asignado a",
                    ),
                ),
                (
                    "activo",
                    models.BooleanField(default=True, verbose_name="Activo"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Creado"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Actualizado"),
                ),
            ],
            options={
                "verbose_name": "Lead",
                "verbose_name_plural": "Leads",
                "ordering": ["-created_at"],
            },
        ),
    ]

# Generated by Django 5.1.6 on 2025-03-01 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reserva_sala', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usuario',
            name='apellido',
        ),
        migrations.RemoveField(
            model_name='usuario',
            name='nombre',
        ),
        migrations.AlterField(
            model_name='usuario',
            name='first_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='last_name',
            field=models.CharField(max_length=100),
        ),
    ]

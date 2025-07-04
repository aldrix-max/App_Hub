# Generated by Django 5.1.3 on 2025-06-17 03:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agent',
            options={'ordering': ['role', 'name'], 'verbose_name': 'Agent', 'verbose_name_plural': 'Agents'},
        ),
        migrations.RemoveField(
            model_name='agent',
            name='user',
        ),
        migrations.AddField(
            model_name='agent',
            name='email',
            field=models.EmailField(default='abc@gmail.com', max_length=254, unique=True, verbose_name="Email de l'agent"),
        ),
        migrations.AddField(
            model_name='agent',
            name='first_name',
            field=models.CharField(default='', max_length=100, verbose_name="Prénom de l'agent"),
        ),
        migrations.AddField(
            model_name='agent',
            name='name',
            field=models.CharField(default='', max_length=100, verbose_name="Nom de l'agent"),
        ),
        migrations.AddField(
            model_name='agent',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, verbose_name="Numéro de téléphone de l'agent"),
        ),
    ]

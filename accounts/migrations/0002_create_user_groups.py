from django.db import migrations
from django.contrib.auth.models import Group, Permission

def create_groups(apps, schema_editor):
    # Создаем группы
    participant_group, created = Group.objects.get_or_create(name='participant')
    organizer_group, created = Group.objects.get_or_create(name='organizer')
    admin_group, created = Group.objects.get_or_create(name='admin')

def remove_groups(apps, schema_editor):
    # Удаляем группы при откате миграции
    Group.objects.filter(name__in=['participant', 'organizer', 'admin']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ] 
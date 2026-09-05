from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hotel", "0002_room_photo_services"),
    ]

    operations = [
        migrations.AddField(
            model_name="guest",
            name="services_completed",
            field=models.BooleanField(default=False, verbose_name="服务已完成"),
        ),
    ]

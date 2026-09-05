from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("hotel", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="guest",
            name="selected_room_id",
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name="已选房号"),
        ),
        migrations.AddField(
            model_name="room",
            name="photo",
            field=models.ImageField(blank=True, null=True, upload_to="rooms", verbose_name="实景图"),
        ),
        migrations.CreateModel(
            name="HotelService",
            fields=[
                ("id", models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name="编号")),
                ("name", models.CharField(max_length=80, verbose_name="名称")),
                ("group", models.CharField(max_length=40, verbose_name="分组")),
                ("description", models.CharField(blank=True, max_length=200, verbose_name="说明")),
                ("sort", models.IntegerField(default=0, verbose_name="排序")),
            ],
            options={
                "verbose_name": "酒店服务",
                "verbose_name_plural": "酒店服务",
                "ordering": ["sort", "id"],
            },
        ),
        migrations.CreateModel(
            name="GuestServiceChoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="提交时间")),
                (
                    "guest",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="service_choices",
                        to="hotel.guest",
                        verbose_name="住客",
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="choices",
                        to="hotel.hotelservice",
                        verbose_name="服务",
                    ),
                ),
            ],
            options={
                "verbose_name": "住客服务需求",
                "verbose_name_plural": "住客服务需求",
                "ordering": ["-created_at"],
                "unique_together": {("guest", "service")},
            },
        ),
    ]

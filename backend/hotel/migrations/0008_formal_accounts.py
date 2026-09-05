from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hotel", "0007_guest_form_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="account",
            name="password",
            field=models.CharField("密码", max_length=128),
        ),
        migrations.AddField(
            model_name="hotelmeta",
            name="staff_invite_code",
            field=models.CharField("员工邀请码", max_length=16, blank=True, default=""),
        ),
    ]

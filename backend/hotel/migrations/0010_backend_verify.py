from django.db import migrations, models


def activate_hotel_managers(apps, schema_editor):
    Account = apps.get_model("hotel", "Account")
    Account.objects.filter(role="manager", is_owner=False).update(status="active")


class Migration(migrations.Migration):
    dependencies = [
        ("hotel", "0009_account_approval"),
    ]

    operations = [
        migrations.AlterField(
            model_name="account",
            name="role",
            field=models.CharField(
                "角色",
                choices=[("guest", "住客"), ("manager", "酒店管理员"), ("backend", "数据后台")],
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="hotelmeta",
            name="smtp_host",
            field=models.CharField("发信服务器", default="smtp.qq.com", max_length=120, blank=True),
        ),
        migrations.AddField(
            model_name="hotelmeta",
            name="smtp_port",
            field=models.IntegerField("发信端口", default=465),
        ),
        migrations.AddField(
            model_name="hotelmeta",
            name="smtp_user",
            field=models.CharField("发信邮箱", default="", max_length=120, blank=True),
        ),
        migrations.AddField(
            model_name="hotelmeta",
            name="smtp_password",
            field=models.CharField("发信授权码", default="", max_length=120, blank=True),
        ),
        migrations.AddField(
            model_name="hotelmeta",
            name="smtp_use_ssl",
            field=models.BooleanField("SSL", default=True),
        ),
        migrations.CreateModel(
            name="VerifyCode",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.CharField("邮箱", db_index=True, max_length=120)),
                ("purpose", models.CharField("用途", choices=[("register", "注册"), ("login", "登录")], max_length=20)),
                ("code", models.CharField("验证码", max_length=128)),
                ("expires_at", models.DateTimeField("过期时间")),
                ("used", models.BooleanField("已使用", default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"verbose_name": "邮箱验证码", "verbose_name_plural": "邮箱验证码"},
        ),
        migrations.CreateModel(
            name="CaptchaChallenge",
            fields=[
                ("id", models.CharField(max_length=32, primary_key=True, serialize=False)),
                ("code", models.CharField(max_length=16)),
                ("expires_at", models.DateTimeField()),
                ("used", models.BooleanField(default=False)),
            ],
            options={"verbose_name": "图形验证码", "verbose_name_plural": "图形验证码"},
        ),
        migrations.RunPython(activate_hotel_managers, migrations.RunPython.noop),
    ]

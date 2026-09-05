from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hotel", "0008_formal_accounts"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="status",
            field=models.CharField(
                "审核状态",
                choices=[("active", "已通过"), ("pending", "待审核"), ("rejected", "已拒绝")],
                default="active",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="account",
            name="is_owner",
            field=models.BooleanField("主管理员", default=False),
        ),
    ]

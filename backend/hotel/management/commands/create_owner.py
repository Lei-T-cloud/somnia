from django.core.management.base import BaseCommand, CommandError

from hotel.security import ensure_owner, valid_email


class Command(BaseCommand):
    help = "写入主管理员账号（密码从命令行传入，不写进代码）"

    def add_arguments(self, parser) -> None:
        parser.add_argument("--email", required=True)
        parser.add_argument("--nickname", required=True)
        parser.add_argument("--password", required=True)

    def handle(self, *args, **options) -> None:
        email = str(options["email"]).strip().lower()
        nickname = str(options["nickname"]).strip()
        password = str(options["password"])
        if not valid_email(email):
            raise CommandError("邮箱格式不正确")
        if len(password) < 8:
            raise CommandError("密码至少 8 位")
        if not nickname:
            raise CommandError("请填写昵称")
        account = ensure_owner(email, nickname, password)
        self.stdout.write(self.style.SUCCESS(f"主管理员已就绪：{account.nickname} <{account.email}>"))

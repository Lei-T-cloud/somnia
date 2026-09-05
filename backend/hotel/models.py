import json

from django.db import models


class Account(models.Model):
    email = models.CharField("邮箱", max_length=120, primary_key=True)
    password = models.CharField("密码", max_length=120)
    role = models.CharField("角色", max_length=20, choices=[("guest", "住客"), ("manager", "管理员")])
    nickname = models.CharField("昵称", max_length=80)

    class Meta:
        verbose_name = "前台账号"
        verbose_name_plural = "前台账号"

    def __str__(self) -> str:
        return f"{self.nickname} ({self.email})"


class GuestAccount(Account):
    class Meta:
        proxy = True
        verbose_name = "客户账号"
        verbose_name_plural = "客户账号"


class ManagerAccount(Account):
    class Meta:
        proxy = True
        verbose_name = "酒店管理员账号"
        verbose_name_plural = "酒店管理员账号"


class SessionToken(models.Model):
    token = models.CharField(max_length=64, primary_key=True)
    email = models.CharField(max_length=120, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "登录令牌"
        verbose_name_plural = "登录令牌"


class Guest(models.Model):
    GENDER = [("female", "女"), ("male", "男"), ("other", "不愿透露")]
    AGE = [("18-25", "18–25"), ("26-35", "26–35"), ("36-50", "36–50"), ("51+", "51 及以上")]
    SCENE = [("business", "商务"), ("wellness", "康养"), ("family", "亲子"), ("leisure", "休闲")]
    LIGHT = [("dark", "全黑"), ("dim", "微光"), ("nightlight", "夜灯")]
    SOUND = [("silent", "绝对安静"), ("white-noise", "白噪音"), ("soft-music", "轻音乐")]
    FIRM = [("soft", "软"), ("medium", "适中"), ("firm", "硬")]

    email = models.CharField("提交账号", max_length=120, primary_key=True)
    nickname = models.CharField("昵称", max_length=80)
    preference_json = models.TextField("偏好 JSON", blank=True, null=True)
    portrait_json = models.TextField("画像 JSON", blank=True, null=True)
    selected_room_id = models.CharField("已选房号", max_length=8, blank=True, null=True)
    services_completed = models.BooleanField("服务已完成", default=False)
    updated_at = models.CharField("更新时间", max_length=40, blank=True, null=True)
    preference_at = models.DateTimeField("确认上传时间", blank=True, null=True)
    room_selected_at = models.DateTimeField("选房时间", blank=True, null=True)
    services_at = models.DateTimeField("服务提交时间", blank=True, null=True)
    gender = models.CharField("性别", max_length=20, choices=GENDER, blank=True)
    age_group = models.CharField("年龄段", max_length=20, choices=AGE, blank=True)
    stay_scene = models.CharField("入住场景", max_length=20, choices=SCENE, blank=True)
    bedtime = models.CharField("就寝时间", max_length=8, blank=True)
    wakeup = models.CharField("起床时间", max_length=8, blank=True)
    preferred_temp = models.FloatField("偏好温度", blank=True, null=True)
    preferred_humidity = models.IntegerField("偏好湿度", blank=True, null=True)
    light = models.CharField("光线", max_length=20, choices=LIGHT, blank=True)
    sound = models.CharField("声音", max_length=20, choices=SOUND, blank=True)
    pillow = models.CharField("枕头硬度", max_length=20, choices=FIRM, blank=True)
    mattress = models.CharField("床垫软硬", max_length=20, choices=FIRM, blank=True)
    issues = models.CharField("睡眠问题", max_length=120, blank=True)
    fragrance = models.CharField("香氛", max_length=80, blank=True)
    bedtime_habit = models.CharField("睡前习惯", max_length=200, blank=True)
    scene_title = models.CharField("睡眠场景", max_length=40, blank=True)

    class Meta:
        verbose_name = "住户偏好"
        verbose_name_plural = "住户偏好"

    def __str__(self) -> str:
        return self.nickname

    @property
    def scene_name(self) -> str:
        if self.scene_title:
            return self.scene_title
        if not self.portrait_json:
            return "未生成"
        try:
            return json.loads(self.portrait_json).get("sceneName") or "未生成"
        except json.JSONDecodeError:
            return "未生成"

    @property
    def has_preference(self) -> bool:
        return bool(self.preference_json)

    @property
    def service_count(self) -> int:
        return self.service_choices.count()


class Room(models.Model):
    id = models.CharField("房号", max_length=8, primary_key=True)
    floor = models.IntegerField("楼层")
    name = models.CharField("名称", max_length=40)
    occupied = models.BooleanField("在住", default=False)
    guest_email = models.CharField("住客邮箱", max_length=120, blank=True, null=True)
    scene_applied = models.BooleanField("场景已应用", default=False)
    env_json = models.TextField("环境 JSON")
    devices_json = models.TextField("设备 JSON")
    history_json = models.TextField("温度历史 JSON")
    photo = models.ImageField("实景图", upload_to="rooms", blank=True, null=True)
    photo_updated_at = models.DateTimeField("实景更新时间", blank=True, null=True)

    class Meta:
        verbose_name = "客房"
        verbose_name_plural = "客房"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.name

    @property
    def current_temp(self) -> float:
        try:
            return float(json.loads(self.env_json).get("temp", 0))
        except json.JSONDecodeError:
            return 0


class GuestStay(models.Model):
    STATUS = [("checked_in", "已入住"), ("checked_out", "已退房")]

    guest_email = models.CharField("客户邮箱", max_length=120, unique=True)
    nickname = models.CharField("客户", max_length=80)
    room_id = models.CharField("所选房间", max_length=8)
    status = models.CharField("入住状态", max_length=20, choices=STATUS, default="checked_in", db_index=True)
    selected_at = models.DateTimeField("选房时间", blank=True, null=True)
    checked_out_at = models.DateTimeField("退房时间", blank=True, null=True)

    class Meta:
        verbose_name = "客户选房"
        verbose_name_plural = "客户选房"
        ordering = ["status", "room_id"]

    def __str__(self) -> str:
        return f"{self.nickname} · {self.room_id} · {self.get_status_display()}"


class HotelService(models.Model):
    id = models.CharField("编号", max_length=40, primary_key=True)
    name = models.CharField("名称", max_length=80)
    group = models.CharField("分组", max_length=40)
    description = models.CharField("说明", max_length=200, blank=True)
    sort = models.IntegerField("排序", default=0)

    class Meta:
        verbose_name = "酒店服务"
        verbose_name_plural = "酒店服务"
        ordering = ["sort", "id"]

    def __str__(self) -> str:
        return self.name


class GuestServiceChoice(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name="service_choices", verbose_name="住客")
    service = models.ForeignKey(HotelService, on_delete=models.CASCADE, related_name="choices", verbose_name="服务")
    created_at = models.DateTimeField("提交时间", auto_now_add=True)

    class Meta:
        verbose_name = "住客服务需求"
        verbose_name_plural = "住客服务需求"
        unique_together = ("guest", "service")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.guest_id} · {self.service_id}"


class SleepPreferenceRecord(models.Model):
    GENDER = [("female", "女"), ("male", "男"), ("other", "不愿透露")]
    AGE = [("18-25", "18–25"), ("26-35", "26–35"), ("36-50", "36–50"), ("51+", "51 及以上")]
    SCENE = [("business", "商务"), ("wellness", "康养"), ("family", "亲子"), ("leisure", "休闲")]
    LIGHT = [("dark", "全黑"), ("dim", "微光"), ("nightlight", "夜灯")]
    SOUND = [("silent", "绝对安静"), ("white-noise", "白噪音"), ("soft-music", "轻音乐")]
    FIRM = [("soft", "软"), ("medium", "适中"), ("firm", "硬")]

    guest = models.OneToOneField(Guest, on_delete=models.CASCADE, related_name="pref_record", verbose_name="住客")
    gender = models.CharField("性别", max_length=20, choices=GENDER, blank=True)
    age_group = models.CharField("年龄段", max_length=20, choices=AGE, blank=True)
    stay_scene = models.CharField("入住场景", max_length=20, choices=SCENE, blank=True)
    bedtime = models.CharField("就寝", max_length=8, blank=True)
    wakeup = models.CharField("起床", max_length=8, blank=True)
    preferred_temp = models.FloatField("偏好温度", blank=True, null=True)
    preferred_humidity = models.IntegerField("偏好湿度", blank=True, null=True)
    light = models.CharField("光线", max_length=20, choices=LIGHT, blank=True)
    sound = models.CharField("声音", max_length=20, choices=SOUND, blank=True)
    pillow = models.CharField("枕头", max_length=20, choices=FIRM, blank=True)
    mattress = models.CharField("床垫", max_length=20, choices=FIRM, blank=True)
    issues = models.CharField("睡眠问题", max_length=120, blank=True)
    fragrance = models.CharField("香氛", max_length=80, blank=True)
    bedtime_habit = models.CharField("睡前习惯", max_length=200, blank=True)
    scene_name = models.CharField("生成场景", max_length=40, blank=True)
    uploaded_at = models.DateTimeField("上传时间", blank=True, null=True)

    class Meta:
        verbose_name = "睡眠偏好"
        verbose_name_plural = "睡眠偏好"

    def __str__(self) -> str:
        return f"{self.guest_id} · {self.scene_name or '未生成'}"


class GuestUpload(models.Model):
    KIND = [
        ("preference", "睡眠偏好"),
        ("select_room", "确认选房"),
        ("services", "酒店服务"),
        ("photo", "客房实景"),
    ]
    kind = models.CharField("类型", max_length=20, choices=KIND, db_index=True)
    guest_email = models.CharField("住客邮箱", max_length=120, blank=True, db_index=True)
    room_id = models.CharField("房号", max_length=8, blank=True, db_index=True)
    summary = models.CharField("摘要", max_length=200)
    payload_json = models.TextField("明细 JSON", blank=True)
    created_at = models.DateTimeField("时间", auto_now_add=True)

    class Meta:
        verbose_name = "上传流水"
        verbose_name_plural = "上传流水"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_kind_display()} · {self.summary}"


class HotelMeta(models.Model):
    id = models.IntegerField(primary_key=True, default=1)
    simulating = models.BooleanField("仿真运行中", default=True)
    trend_json = models.TextField("趋势 JSON", default="[]")

    class Meta:
        verbose_name = "仿真状态"
        verbose_name_plural = "仿真状态"

    def __str__(self) -> str:
        return "运行中" if self.simulating else "已暂停"

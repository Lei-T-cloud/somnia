import json

from django.contrib import admin
from django.utils.html import format_html

from .models import Guest, GuestAccount, GuestServiceChoice, GuestStay, GuestUpload, HotelMeta, HotelService, ManagerAccount, Room, SleepPreferenceRecord
from .stays import check_in, checkout_guest


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = (
        "nickname",
        "gender",
        "age_group",
        "stay_scene",
        "bedtime",
        "wakeup",
        "preferred_temp",
        "preferred_humidity",
        "light",
        "sound",
        "preference_at",
    )
    list_filter = ("gender", "age_group", "stay_scene", "light", "sound", "pillow", "mattress")
    search_fields = ("email", "nickname", "fragrance", "bedtime_habit", "issues")
    list_per_page = 20
    readonly_fields = (
        "email",
        "nickname",
        "gender",
        "age_group",
        "stay_scene",
        "bedtime",
        "wakeup",
        "preferred_temp",
        "preferred_humidity",
        "light",
        "sound",
        "pillow",
        "mattress",
        "issues",
        "fragrance",
        "bedtime_habit",
        "preference_at",
    )
    fieldsets = (
        ("个人信息", {"fields": ("nickname", "gender", "age_group", "stay_scene")}),
        (
            "睡眠偏好",
            {
                "fields": (
                    ("bedtime", "wakeup"),
                    ("preferred_temp", "preferred_humidity"),
                    ("light", "sound"),
                    ("pillow", "mattress"),
                    "issues",
                    "fragrance",
                    "bedtime_habit",
                    "preference_at",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .exclude(preference_json__isnull=True)
            .exclude(preference_json="")
        )


@admin.register(GuestStay)
class GuestStayAdmin(admin.ModelAdmin):
    list_display = ("nickname", "guest_email", "room_id", "status_label", "selected_at", "checked_out_at")
    list_filter = ("status", "room_id")
    search_fields = ("nickname", "guest_email", "room_id")
    list_per_page = 20
    readonly_fields = ("selected_at", "checked_out_at")
    actions = ["mark_checked_out", "mark_checked_in"]
    fields = ("nickname", "guest_email", "room_id", "status", "selected_at", "checked_out_at")

    @admin.display(description="状态", ordering="status")
    def status_label(self, obj: GuestStay) -> str:
        if obj.status == "checked_in":
            return format_html('<span style="color:#1f9d55;font-weight:700">已入住</span>')
        return format_html('<span style="color:#c45611;font-weight:700">已退房</span>')

    @admin.action(description="标记为已退房")
    def mark_checked_out(self, request, queryset):
        for stay in queryset:
            checkout_guest(stay.guest_email)

    @admin.action(description="标记为已入住")
    def mark_checked_in(self, request, queryset):
        for stay in queryset:
            room = Room.objects.filter(id=stay.room_id).first()
            if room and room.guest_email and room.guest_email != stay.guest_email:
                continue
            guest = Guest.objects.filter(email=stay.guest_email).first()
            if guest:
                guest.selected_room_id = stay.room_id
                guest.save(update_fields=["selected_room_id"])
            if room:
                room.occupied = True
                room.guest_email = stay.guest_email
                room.save(update_fields=["occupied", "guest_email"])
            check_in(stay.guest_email, stay.nickname, stay.room_id)


@admin.register(SleepPreferenceRecord)
class SleepPreferenceRecordAdmin(admin.ModelAdmin):
    list_display = ("guest", "stay_scene", "preferred_temp", "preferred_humidity", "light", "sound", "scene_name", "uploaded_at")
    list_filter = ("stay_scene", "gender", "age_group", "light", "sound")
    search_fields = ("guest__email", "guest__nickname", "fragrance", "bedtime_habit", "scene_name")
    readonly_fields = ("uploaded_at",)


@admin.register(GuestUpload)
class GuestUploadAdmin(admin.ModelAdmin):
    list_display = ("created_at", "kind", "guest_email", "room_id", "summary")
    list_filter = ("kind", "room_id")
    search_fields = ("guest_email", "room_id", "summary")
    date_hierarchy = "created_at"
    readonly_fields = ("kind", "guest_email", "room_id", "summary", "payload_preview", "payload_json", "created_at")

    @admin.display(description="明细")
    def payload_preview(self, obj: GuestUpload) -> str:
        return _pretty_json(obj.payload_json)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "floor", "occupied", "guest_email", "scene_applied", "current_temp", "photo_thumb", "photo_updated_at")
    list_filter = ("floor", "occupied", "scene_applied")
    search_fields = ("id", "guest_email", "name")
    readonly_fields = ("current_temp", "photo_thumb", "photo_updated_at")
    fieldsets = (
        ("客房", {"fields": ("id", "floor", "name")}),
        ("入住与场景", {"fields": ("occupied", "guest_email", "scene_applied", "current_temp")}),
        ("实景图", {"fields": ("photo", "photo_thumb", "photo_updated_at")}),
        ("仿真快照", {"classes": ("collapse",), "fields": ("env_json", "devices_json", "history_json")}),
    )

    @admin.display(description="实景")
    def photo_thumb(self, obj: Room) -> str:
        if not obj.photo:
            return "未上传"
        return format_html('<img src="{}" alt="{}" style="height:56px;border-radius:6px;object-fit:cover" />', obj.photo.url, obj.name)


@admin.register(HotelService)
class HotelServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "group", "sort")
    list_filter = ("group",)
    search_fields = ("id", "name", "description")
    list_editable = ("sort",)
    ordering = ("sort", "id")


@admin.register(GuestServiceChoice)
class GuestServiceChoiceAdmin(admin.ModelAdmin):
    list_display = ("guest", "room_id", "service", "group", "completed", "created_at")
    list_filter = ("service__group", "guest__services_completed", "guest__selected_room_id")
    search_fields = ("guest__email", "guest__nickname", "service__name", "guest__selected_room_id")
    autocomplete_fields = ("guest", "service")

    @admin.display(description="房号", ordering="guest__selected_room_id")
    def room_id(self, obj: GuestServiceChoice) -> str:
        return obj.guest.selected_room_id or "—"

    @admin.display(description="分组", ordering="service__group")
    def group(self, obj: GuestServiceChoice) -> str:
        return obj.service.group

    @admin.display(description="已完成", boolean=True, ordering="guest__services_completed")
    def completed(self, obj: GuestServiceChoice) -> bool:
        return obj.guest.services_completed


class AccountRoleAdmin(admin.ModelAdmin):
    role = ""
    list_display = ("email", "nickname")
    search_fields = ("email", "nickname")
    fields = ("email", "nickname", "password")

    def get_queryset(self, request):
        return super().get_queryset(request).filter(role=self.role)

    def save_model(self, request, obj, form, change):
        from .security import is_hashed, hash_password, sync_backend_user

        obj.role = self.role
        if obj.password and not is_hashed(obj.password):
            obj.password = hash_password(obj.password)
        super().save_model(request, obj, form, change)
        if obj.role == "manager":
            sync_backend_user(obj)


@admin.register(GuestAccount)
class GuestAccountAdmin(AccountRoleAdmin):
    role = "guest"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        Guest.objects.get_or_create(email=obj.email, defaults={"nickname": obj.nickname})


@admin.register(ManagerAccount)
class ManagerAccountAdmin(AccountRoleAdmin):
    role = "manager"
    list_display = ("email", "nickname", "status", "is_owner")
    list_filter = ("status", "is_owner")
    fields = ("email", "nickname", "password", "status", "is_owner")
    actions = ["approve_staff", "reject_staff"]

    @admin.action(description="通过并允许进入管理端")
    def approve_staff(self, request, queryset):
        from .security import sync_backend_user

        for account in queryset.exclude(is_owner=True):
            account.status = "active"
            account.save(update_fields=["status"])
            sync_backend_user(account)

    @admin.action(description="拒绝进入管理端")
    def reject_staff(self, request, queryset):
        from .models import SessionToken
        from .security import sync_backend_user

        for account in queryset.exclude(is_owner=True):
            account.status = "rejected"
            account.save(update_fields=["status"])
            SessionToken.objects.filter(email=account.email).delete()
            sync_backend_user(account)


@admin.register(HotelMeta)
class HotelMetaAdmin(admin.ModelAdmin):
    list_display = ("id", "simulating")


def _pretty_json(raw: str | None):
    if not raw:
        return "—"
    try:
        text = json.dumps(json.loads(raw), ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        text = raw
    return format_html("<pre style='white-space:pre-wrap;max-width:720px;margin:0'>{}</pre>", text)

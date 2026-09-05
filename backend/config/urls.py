from pathlib import Path

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import redirect
from django.urls import include, path, re_path
from django.views.static import serve as static_serve

admin.site.site_header = "眠栖 Somnia 后台"
admin.site.site_title = "眠栖管理"
admin.site.index_title = "数字孪生数据管理"


def spa_index(_request, rest: str = ""):
    frontend = Path(settings.FRONTEND_DIR)
    index = frontend / "index.html"
    if index.exists():
        return FileResponse(index.open("rb"), content_type="text/html")
    if rest:
        raise Http404("前台尚未打包")
    return redirect("/admin/")


def health(_request):
    return HttpResponse('{"ok":true,"service":"somnia-django"}', content_type="application/json")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health", health),
    path("api/", include("hotel.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

frontend = Path(getattr(settings, "FRONTEND_DIR", ""))
if frontend.exists():
    urlpatterns += [
        re_path(r"^assets/(?P<path>.*)$", static_serve, {"document_root": frontend / "assets"}),
        re_path(r"^(?P<path>login-bg\.jpg)$", static_serve, {"document_root": frontend}),
    ]

urlpatterns += [
    path("", spa_index),
    re_path(r"^(?!api/|admin/|media/|static/).*$", spa_index),
]

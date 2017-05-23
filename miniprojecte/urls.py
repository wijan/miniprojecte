from django.conf.urls.static import static
from django.conf.urls import url, include
from django.conf import settings

urlpatterns =([
    url(r'^', include('testsforall.urls', namespace="testsforall")),
    ]
    + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('documents/', include('documents.urls')),
    path('chatbots/', include('chatbots.urls')),
    path('', include('home.urls')),  # Startseite oder andere Apps
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
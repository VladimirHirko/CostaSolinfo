from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Импорт всех нужных View
from core.views import (
    HomepageView,
    InfoMeetingView,
    AirportTransferView,
    QuestionView,
    ContactInfoView,
    AboutUsView,
    ExcursionView,
)

urlpatterns = [
    path('grappelli/', include('grappelli.urls')),  # Grappelli UI
    path('admin/', admin.site.urls),

    # 🔹 API endpoints
    path('api/homepage/', HomepageView.as_view(), name='homepage'),
    path('api/info-meeting/', InfoMeetingView.as_view(), name='info-meeting'),
    path('api/airport-transfer/', AirportTransferView.as_view(), name='airport-transfer'),
    path('api/question/', QuestionView.as_view(), name='question'),
    path('api/contact-info/', ContactInfoView.as_view(), name='contact-info'),
    path('api/about-us/', AboutUsView.as_view(), name='about-us'),
    path('api/excursion/', ExcursionView.as_view(), name='excursion'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

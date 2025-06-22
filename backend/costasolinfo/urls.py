from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views
# Импорт всех нужных View
from core.views import (
    HomepageView, InfoMeetingView, AirportTransferView, QuestionView,
    ContactInfoView, AboutUsView, ExcursionView, TransferScheduleLookupView,
    page_banner_api
)

urlpatterns = [
    path('grappelli/', include('grappelli.urls')),  # Grappelli UI
    path('admin/', admin.site.urls),

    # 🔹 API endpoints
    path('api/banner/<str:page>/', page_banner_api, name='page_banner_api'),
    path('api/homepage/', HomepageView.as_view(), name='homepage'),
    path('api/info-meeting/', InfoMeetingView.as_view(), name='info-meeting'),
    path('api/airport-transfer/', AirportTransferView.as_view(), name='airport-transfer'),
    path('api/question/', QuestionView.as_view(), name='question'),
    path('api/contact-info/', ContactInfoView.as_view(), name='contact-info'),
    path('api/about-us/', AboutUsView.as_view(), name='about-us'),
    path('api/excursion/', ExcursionView.as_view(), name='excursion'),
    path('api/transfer-schedule/', TransferScheduleLookupView.as_view(), name='transfer-schedule'),
    path('api/hotels/', views.hotel_search, name='hotel_search'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

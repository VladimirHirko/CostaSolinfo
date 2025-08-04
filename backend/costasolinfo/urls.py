from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from core import views
# Импорт всех нужных View
from core.views import (
    HomepageView, InfoMeetingView, AirportTransferView, QuestionView,
    ContactInfoView, AboutUsView, ExcursionView, TransferScheduleLookupView,
    page_banner_api, BulkTransferScheduleForm, transfer_info, transfer_schedule_view,
    available_hotels_for_transfer, TransferNotificationViewSet, TransferInquiryViewSet,
    confirm_transfer_notification, PrivacyPolicyView, info_meeting_schedule,
    ExcursionListView, PageBannerView, ExcursionDetailView, pickup_point_detail,
    excursion_pickup_view
)

transfer_notification_view = TransferNotificationViewSet.as_view({'post': 'create'})



router = DefaultRouter()
router.register(r'transfer-inquiries', TransferInquiryViewSet, basename='transfer-inquiries')
router.register(r'transfer-notifications', TransferNotificationViewSet, basename='transfer-notifications')


urlpatterns = [
    path('grappelli/', include('grappelli.urls')),  # Grappelli UI
    path('admin/', admin.site.urls),

    # 🔹 API endpoints
    path('api/banner/<str:page>/', page_banner_api, name='page_banner_api'),
    path("api/banner/<str:page>/", PageBannerView.as_view(), name="page-banner"),
    path('api/homepage/', HomepageView.as_view(), name='homepage'),
    path('api/info-meeting/', InfoMeetingView.as_view(), name='info-meeting'),
    path('api/info-meetings/', info_meeting_schedule, name='info-meeting-schedule'),
    path('api/airport-transfer/', AirportTransferView.as_view(), name='airport-transfer'),
    path('api/transfer-info/', transfer_info, name='transfer_info'),
    path('api/transfer-schedule/', transfer_schedule_view, name='transfer_schedule'),
    path('api/transfer-notifications/', transfer_notification_view, name='transfer-notification'),
    path('api/transfer-confirm/<uuid:token>/', confirm_transfer_notification, name='transfer_confirm'),
    path('api/available-hotels/', available_hotels_for_transfer, name='available_hotels_for_transfer'),
    path('api/question/', QuestionView.as_view(), name='question'),
    path('api/contact-info/', ContactInfoView.as_view(), name='contact-info'),
    path('api/about-us/', AboutUsView.as_view(), name='about-us'),
    path('api/excursion/', ExcursionView.as_view(), name='excursion'),
    path('api/excursions/', ExcursionListView.as_view(), name='excursion-list'),
    path("api/excursions/<int:pk>/", ExcursionDetailView.as_view(), name="excursion-detail"),
    path("api/excursions/<int:excursion_id>/pickup/", excursion_pickup_view, name="excursion_pickup"),
    path("api/pickup-point/<int:pk>/", pickup_point_detail, name="pickup_point_detail"),
    #path('api/transfer-schedule/', TransferScheduleLookupView.as_view(), name='transfer-schedule'),
    path('api/', include(router.urls)),
    path('api/hotels/', views.hotel_search, name='hotel_search'),
    path('api/privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
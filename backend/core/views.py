from rest_framework.generics import RetrieveAPIView
from core.models import Homepage, InfoMeeting, AirportTransfer, Question, ContactInfo, AboutUs, Excursion
from .serializers import (
    HomepageSerializer, InfoMeetingSerializer, AirportTransferSerializer,
    QuestionSerializer, ContactInfoSerializer, AboutUsSerializer, ExcursionSerializer
)

# Главное правило: RetrieveAPIView + queryset + serializer_class

class HomepageView(RetrieveAPIView):
    queryset = Homepage.objects.all()
    serializer_class = HomepageSerializer

    def get_object(self):
        return self.queryset.first()

class InfoMeetingView(RetrieveAPIView):
    queryset = InfoMeeting.objects.all()
    serializer_class = InfoMeetingSerializer

    def get_object(self):
        return self.queryset.first()

class AirportTransferView(RetrieveAPIView):
    queryset = AirportTransfer.objects.all()
    serializer_class = AirportTransferSerializer

    def get_object(self):
        return self.queryset.first()

class QuestionView(RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_object(self):
        return self.queryset.first()

class ContactInfoView(RetrieveAPIView):
    queryset = ContactInfo.objects.all()
    serializer_class = ContactInfoSerializer

    def get_object(self):
        return self.queryset.first()

class AboutUsView(RetrieveAPIView):
    queryset = AboutUs.objects.all()
    serializer_class = AboutUsSerializer

    def get_object(self):
        return self.queryset.first()

class ExcursionView(RetrieveAPIView):
    queryset = Excursion.objects.all()
    serializer_class = ExcursionSerializer

    def get_object(self):
        return self.queryset.first()  # если только одна экскурсия, иначе делаем ListAPIView

from modeltranslation.translator import register, TranslationOptions
from .models import Homepage, InfoMeeting, AirportTransfer, Question, ContactInfo, AboutUs, Excursion

# Главная
@register(Homepage)
class HomepageTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle')

# Инфо встреча
@register(InfoMeeting)
class InfoMeetingTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'location')

# Трансфер в аэропорт
@register(AirportTransfer)
class AirportTransferTranslationOptions(TranslationOptions):
    fields = ('description', 'pickup_location')

# Задать вопрос
@register(Question)
class QuestionTranslationOptions(TranslationOptions):
    fields = ('message',)

# Контакты
@register(ContactInfo)
class ContactInfoTranslationOptions(TranslationOptions):
    fields = ('office_name', 'address')

# О нас
@register(AboutUs)
class AboutUsTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

# Экскурсии
@register(Excursion)
class ExcursionTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

from modeltranslation.translator import register, TranslationOptions, translator
from .models import (
    Homepage, InfoMeeting, AirportTransfer, 
    Question, ContactInfo, AboutUs, Excursion, 
    ExcursionContentBlock
)

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
    fields = ('question',)

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
    fields = ('title',)

# Блоки контента экскурсии
class ExcursionContentBlockTranslationOptions(TranslationOptions):
    fields = ('title', 'content')

translator.register(ExcursionContentBlock, ExcursionContentBlockTranslationOptions)

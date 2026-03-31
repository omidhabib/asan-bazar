from .translations import TRANSLATIONS

def translation_processor(request):
    # Get language from Django's current language (set by LocaleMiddleware)
    from django.utils import translation
    lang = translation.get_language()
    if lang:
        lang = lang.split('-')[0]
    else:
        lang = 'en'
    
    return {'t': TRANSLATIONS.get(lang, TRANSLATIONS['en'])}

def google_maps_api_key(request):
    from django.conf import settings
    return {'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', 'YOUR_API_KEY_HERE')}

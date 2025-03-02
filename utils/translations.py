"""
Utility module for handling translations in the application.
"""
import gettext

# Set up the translation function
_translations = {}
_ = gettext.gettext  # Original gettext function

def setup_translations(locale_dir, language='en'):
    """Set up translations for the given language."""
    global _
    translation = gettext.translation('all-in-run', localedir=locale_dir, 
                                     languages=[language], fallback=True)
    _ = translation.gettext
    return _

def translate(text, domain=None):
    """
    Translate the given text string.
    
    Args:
        text: Text to translate
        domain: Optional domain for context-specific translations
    
    Returns:
        Translated text
    """
    if domain and domain in _translations:
        return _translations[domain].get(text, text)
    return _(text) if text else text

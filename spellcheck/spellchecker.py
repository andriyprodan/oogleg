import hunspell
from django.conf import settings

# Create a Hunspell object and specify the path to the dictionary files
hobj = hunspell.HunSpell(str(settings.BASE_DIR / 'spellcheck/dictionaries/uk_UA/uk_UA.dic'),
                         str(settings.BASE_DIR / 'spellcheck/dictionaries/uk_UA/uk_UA.aff'))


def correct_text(text):
    words = text.split(' ')
    for word in words:
        if not hobj.spell(word):
            suggestions = hobj.suggest(word)
            if suggestions:
                text = text.replace(word, suggestions[0])
    return text

### DAILY CHALLENGE - TRANSLATOR - DAY 1 WEEK 5

# ##### >>>>>>> Python 3.13 compatibility issue 
# # The traceback tells us that httpx (used by googletrans) is importing the built-in cgi module, which was removed in Python 3.13.
# # Because googletrans → httpx → cgi, the import chain breaks with:
# # ModuleNotFoundError: No module named 'cgi'

# # import types, sys
# # sys.modules['cgi'] = types.ModuleType('cgi')

# from googletrans import Translator

# # Instructions :
# # Consider this list

# # french_words= ["Bonjour", "Au revoir", "Bienvenue", "A bientôt"] 
# # Look at this result :
# # {"Bonjour": "Hello", "Au revoir": "Goodbye", "Bienvenue": "Welcome", "A bientôt": "See you soon"}
# # You have to recreate the result using a translator module. Take a look at the googletrans module

# # Liste de mots français
# french_words = ["Bonjour", "Au revoir", "Bienvenue", "A bientôt"]

# # Crée le traducteur
# translator = Translator()

# # Traduit chaque mot du français vers l’anglais
# translations = {word: translator.translate(word, src='fr', dest='en').text for word in french_words}

# # Affiche le dictionnaire résultat
# print(translations)


"""Instructions :

Consider this list

french_words= ["Bonjour", "Au revoir", "Bienvenue", "A bientôt"] 
Look at this result :
{"Bonjour": "Hello", "Au revoir": "Goodbye", "Bienvenue": "Welcome", "A bientôt": "See you soon"}"""


from googletrans import Translator
import asyncio


async def TranslateText(text):
  async with Translator() as translator:
    result = await translator.translate(text, src="fr", dest="en")
    return result.text

french_words= ["Bonjour", "Au revoir", "Bienvenue", "A bientôt"] 

text ="Bonjour"
dict_trad = {}

for word in french_words:
  dict_trad[word] = asyncio.run(TranslateText(word))
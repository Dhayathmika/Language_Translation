from django.shortcuts import render
from googletrans import Translator
from gtts.langs import _main_langs
import speech_recognition as sr
from io import BytesIO
from gtts import gTTS
import pygame
import time

def home(request):
    return render(request,'home.html')

def translate(request):
    dict = {}
    if request.method == 'POST':
        input_language = request.POST.get('input_language', 'en')
        translator_language = request.POST.get('translator_language', 'de')
        dict['input_language'] = input_language
        dict['translator_language'] = translator_language
        return dict
    else:
        render(request,'translator.html')

def translator(request):
    global input_language
    global translator_language
    if request.method == 'POST':
        input_language = request.POST.get('input_language', '')
        translator_language = request.POST.get('translator_language', '')
        if input_language in _main_langs():
            input_value = _main_langs()[input_language]
        if translator_language in _main_langs():
            translator_value = _main_langs()[translator_language]
        return render(request, 'translator.html', {'input_language': input_value, 'translator_language': translator_value})
    else:
        return render(request, 'home.html')

# SPEECH TO TEXT
def speech_to_text(request, language='en'):
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 3000

    try:
        with sr.Microphone() as source:
            audio = recognizer.listen(source)

        text = recognizer.recognize_google(audio, language=language)
        return text
    except sr.UnknownValueError:
        return render(request, 'translator.html', {'success': False, 'error': 'Sorry, could not understand audio.'})
    except sr.RequestError as e:
        return render(request, 'translator.html', {'success': False, 'error': f"Error with Google Web Speech API; {e}"})

# TRANSLATOR MODEL
def translate_text(request, text, src_lang='en', dest_lang='de', max_retries=3):
    translator = Translator()

    for i in range(max_retries):
        try:
            translated_text = translator.translate(text, src=src_lang, dest=dest_lang).text
            return translated_text

        except Exception as e:
            print(f"Translation error: {e}")
            if 'Did not match any source language' in str(e) or '429 (Too Many Requests)' in str(e):
                print("Retrying after a short delay...")
                time.sleep(1)
                continue
            else:
                break
    return render(request, 'translator.html', {'success': False, 'error': 'Failed to translate text'})

# TEXT TO SPEECH
def text_to_speech(request):
    if 'button1' in request.POST:
        if input_language in _main_langs():
            input_value = _main_langs()[input_language]
        if translator_language in _main_langs():
            translator_value = _main_langs()[translator_language]
        text = speech_to_text(request, input_language)
        translated_text = translate_text(request, text, input_language, translator_language, 3)
        try:
            mp3_fp = BytesIO()
            tts = gTTS(translated_text, lang=translator_language)
            tts.write_to_fp(mp3_fp)

            pygame.init()
            mp3_fp.seek(0)
            pygame.mixer.init()
            pygame.mixer.music.load(mp3_fp)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(5)
            return render(request, 'translator.html', {'success': True, 'translated_text': translated_text,'input_language':input_value,'translator_language':translator_value})

        except Exception as e:
            return render(request, 'translator.html',
                          {'success': False, 'error': "Please Speak Anything....",'input_language':input_value,'translator_language':translator_value})
    if 'button2' in request.POST:
        if input_language in _main_langs():
            input_value = _main_langs()[input_language]
        if translator_language in _main_langs():
            translator_value = _main_langs()[translator_language]
        text = speech_to_text(request, translator_language)
        translated_text1 = translate_text(request, text, translator_language, input_language, 3)
        try:
            mp3_fp = BytesIO()
            tts = gTTS(translated_text1, lang=input_language)
            tts.write_to_fp(mp3_fp)

            pygame.init()
            mp3_fp.seek(0)
            pygame.mixer.init()
            pygame.mixer.music.load(mp3_fp)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(5)
            return render(request, 'translator.html', {'success': True, 'translated_text1': translated_text1,'input_language':input_value,'translator_language':translator_value})

        except Exception as e:
            return render(request, 'translator.html',{'success': False, 'error1':"Please Speak Anything....",'input_language':input_value,'translator_language':translator_value})


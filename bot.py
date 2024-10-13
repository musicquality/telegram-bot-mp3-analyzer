import telebot
import librosa
from pydub import AudioSegment
import os

# Токен вашего бота
TOKEN = '7853275115:AAExSJywrx0fNljlV6vdPG5cb4obw9bGimA'
bot = telebot.TeleBot(TOKEN)


# Функция для анализа тональности
def get_key(file_path):
    y, sr = librosa.load(file_path)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    key = librosa.key.estimate_tuning(y=y, sr=sr)
    return librosa.hz_to_note(key)


# Преобразование по колесу камелота
def camelot_key(note):
    camelot_wheel = {
        'C': '8B', 'C#': '3B', 'D': '10B', 'D#': '5B',
        'E': '12B', 'F': '7B', 'F#': '2B', 'G': '9B',
        'G#': '4B', 'A': '11B', 'A#': '6B', 'B': '1B'
    }
    return camelot_wheel.get(note, 'Unknown')


@bot.message_handler(content_types=['audio', 'document'])
def handle_audio(message):
    try:
        file_info = bot.get_file(message.audio.file_id if message.audio else message.document.file_id)
        file_path = file_info.file_path
        downloaded_file = bot.download_file(file_path)

        # Сохранение файла на диск
        with open("received_audio.mp3", 'wb') as new_file:
            new_file.write(downloaded_file)

        # Анализ тональности
        key = get_key("received_audio.mp3")
        camelot = camelot_key(key)

        # Переименование файла с кодом по колесу Камелота
        new_filename = f"{camelot}_track.mp3"
        os.rename("received_audio.mp3", new_filename)

        # Отправка переименованного файла обратно пользователю
        with open(new_filename, 'rb') as audio_file:
            bot.send_audio(message.chat.id, audio_file)

        # Удаление временных файлов
        os.remove(new_filename)

    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка при обработке файла.')


# Запуск бота
bot.polling()

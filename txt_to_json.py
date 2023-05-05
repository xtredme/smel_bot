import json

ar = []
def txt_to_json_with_codding(file_name:str):
    formating = ['.txt', '.json']
    file_txt = file_name+formating[0]
    file_json = file_name+formating[1]
    with open(file_txt, encoding='utf-8') as r:
        for i in r:
            n = i.lower().split('\n')[0]
            if n != '':
                ar.append(n)

    with open(file_json, 'w', encoding='utf-8') as e:
        json.dump(ar, e)


def txt_to_json_with_uncodding(file_name: str): # делает из txt файла json и заполняет кирилицей
    formating = ['.txt', '.json']
    file_txt = file_name+formating[0]
    file_json = file_name+formating[1]
    with open(file_txt, encoding='utf-8') as f:
        words = []
        for line in f:
            # Извлекаем слова и приводим к нижнему регистру
            line_words = [word.lower() for word in line.strip().split() if word.isalpha()]
            # Добавляем слова к списку
            words.extend(line_words)

    # Записываем слова в файл bad_words.json
    with open(file_json, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False)

"""Введи название файла txt (без расширения) в папке со скриптом который хочешь
перевести json.

Функция txt_to_json_with_codding('Название файла') сделает закодированый json файл
Функция txt_to_json_with_codding('Название файла') сделает заполненый на кирилице json файл

"""
txt_to_json_with_codding('bad_words')  #Введи название файла txt  в папке со скриптом

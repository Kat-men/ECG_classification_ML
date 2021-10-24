import os
import h5py
import wfdb as wf
import numpy as np
import pandas as pd
from glob import glob
from scipy import signal as ss
from utils import download as ud
from matplotlib import pyplot as plt


def get_records():
    
    # Скачать, если не существует базы 
    if not os.path.isdir('datasets/mitdb'):
        print ('1 Загрузка mitdb database...')
        ud.download_mitdb()
        print ('Загрузка завершена')

    # Для каждой записи существует 3 файла
    # *.atr один из них 
    paths = glob('datasets/mitdb/*.atr')

    # Избавление от расширения
    paths = [path[:-4] for path in paths]
    paths.sort()

    return paths

def good_types():
    
    good = ['N', 'L', 'R', 'B', 'A',
            'a', 'J', 'S', 'V', 'r',
            'F', 'e', 'j', 'n', 'E',
            '/', 'f', 'Q', '?']

    return good

def beat_annotations(annotation):
    # объявление типов ударов
    good = good_types()
    ids = np.in1d(annotation.symbol, good)

    # Информация о положениях ударов с аннотациями
    beats = annotation.sample[ids]

    return beats

def convert_input(channel, annotation):

    # Удалить аннотации без биений
    beats = beat_annotations(annotation)

    # Создание гребня Дирака
    dirac = np.zeros_like(channel)
    dirac[beats] = 1.0

    # Применение окна Хэмминга как фильтра колоколообразной кривой
    width = 36
    filter = ss.hamming(width)
    gauss = np.convolve(filter, dirac, mode = 'same')

    return dirac, gauss

def good_annotations():

    good_annotations = [1, 2, 3, 4,
                        5, 6, 7, 8,
                        9, 10, 11, 12,
                        13, 16, 31, 38]

    return good_annotations

def make_dataset(records, width, savepath):
    """ Внутри массива """
    signals, labels = [], []

    # Итерирование файлов
    for path in records:
        print ('Обработка файла:', path)
        record = wf.rdrecord(path)
        annotations = wf.rdann(path, 'atr')

        # Добавление чистого сигнала
        data = record.p_signal

        # Преобразование каждого канала в помеченные фрагменты
        signal, label = convert_data(data, annotations, width)
        signal

        # Суммирование
        signals.append(signal)
        labels.append(label)

    # Конвертрование в один numpy массив
    signals = np.vstack(signals)
    labels = np.vstack(labels)

    # Запись на диск
    np.save(savepath, {'signals' : signals,
                       'labels'  : labels })

def convert_data(data, annotations, width):
    """ В партии """
    
    signals, labels = [], []

    # Конвертрование обоих каналов 
    for it in range(2):
        channel = data[:, it]
        dirac, gauss = convert_input(channel,
                                     annotations)
        # Объединение ярлыков
        label = np.vstack([dirac, gauss])

        # Подготовка движущеегося окна
        sta = 0
        end = width
        stride = width
        while end <= len(channel):
            # Отрезать фрагменты
            s_frag = channel[sta : end]
            l_frag = label[:, sta : end]

            # Суммирование
            signals.append(s_frag)
            labels.append(l_frag)

            sta += stride
            end += stride

    # Преобразование в массивы
    signals = np.array(signals)
    labels = np.array(labels)

    return signals, labels

def create_datasets():
    """ Тренировка, валидация, тестирование """

    records = get_records()


    # Перетасовать детерминированно
    np.random.seed(666)
    np.random.shuffle(records)

    # Описание данных
    width = 200

    # Создание тренировочного
    make_dataset(records[:30], width, 'datasets/training')

    # ... валидационного ...
    make_dataset(records[30 : 39], width, 'datasets/validation')

    # ... и тестового датасета
    make_dataset(records[39 : 48], width, 'datasets/test')



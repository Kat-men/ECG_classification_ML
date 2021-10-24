import os
from urllib.request import urlopen
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup as BSoup

def download_mitdb():
    
    extensions = ['atr', 'dat', 'hea']
    the_path = 'https://www.physionet.org/content/mitdb/1.0.0/'

    # Сохранить в соответствующие data/mitdb
    savedir = 'data\\mitdb'
    if not os.path.exists(savedir):
        os.makedirs(savedir)

    savename = savedir + '{}.{}'
    
    # Найти все интересующие файлы на сайте 
    soup = BSoup(urlopen(the_path).read())
    

    # Найти все ссылки, указывающие на файлы .dat
    hrefs = []
    for a in soup.find_all('a', href=True):
        
        href = a['href'][-7:]
        
        if href[-4::] == '.dat':
            
            hrefs.append(href[:-4])
    print('hrefs',hrefs)
    # Путь к файлу в интернете
    down_path = the_path + '\\{}.{}'
    
    for data_id in hrefs:
        print('data_id',data_id)
        for ext in extensions:
            print('ext',ext)
            webpath = down_path.format(data_id, ext)
            print(webpath)
            datafile = urlopen(webpath)

            # Сохранить локально
            filepath = savename.format(data_id, ext)
            with open(filepath, 'wb') as out:
                out.write(datafile.read())

    print('Загружены {} '.format(len(hrefs)))



if __name__ == '__main__':
    download_mitdb()

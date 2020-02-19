import os
import requests


API_URL = 'http://localhost:5000/text-paper-analysis/api/v1.0/'
MAX_RETRIES = 60


# 条形码文本读取
def get_barcode(filename):
    files = {'barcode': (filename, open(filename, 'rb'), 'image/png', {})}
    response = requests.post(API_URL + "barcode_text", files=files)
    print('get_barcode> ', response.text)


#def analysis(filename):
#    files = {'text_paper': (filename, open(filename, 'rb'), 'image/png', {})}
#    values = {'template_width': 1000, 'template_height': 700, 'save_dir': '20191121',
#              'objects': [{'name':'n1', 'left':0, 'top':350, 'right':450, 'bottom':370},
#                          {'name':'n2', 'left':0, 'top':370, 'right':450, 'bottom':390},
#                          {'name':'n3', 'left':0, 'top':390, 'right':450, 'bottom':430},
#                          {'name':'n4', 'left':0, 'top':430, 'right':450, 'bottom':530},
#                          {'name':'n5', 'left':520, 'top':0, 'right':975, 'bottom':444}]}
#    response = requests.post(API_URL + "analysis", files=files, data=values)
#    print('analysis> ', response.text)


# 试卷分析
def analysis(filename):
    files = {'text_paper': ('barcode.png', open('barcode.png', 'rb'), 'image/png', {})}
    values = {'text_paper_filename': filename,
              'template_width': 1000,
              'template_height': 700,
              'save_dir': '20191121',
              'objects': [{'name':'n1', 'left':0, 'top':350, 'right':450, 'bottom':370},
                          {'name':'n2', 'left':0, 'top':370, 'right':450, 'bottom':390},
                          {'name':'n3', 'left':0, 'top':390, 'right':450, 'bottom':430},
                          {'name':'n4', 'left':0, 'top':430, 'right':450, 'bottom':530},
                          {'name':'n5', 'left':520, 'top':0, 'right':975, 'bottom':444}]}

    response = requests.post(API_URL + "analysis", files=files, data=values)
    print('analysis> ', response.text)

if __name__ == '__main__':
    get_barcode('barcode.png')
    analysis('test.png')

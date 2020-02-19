import os
import logging
import tempfile
import zipfile

from pyzbar import pyzbar
from PIL import Image

import werkzeug
from flask import Flask, request, jsonify, make_response, redirect, url_for
from flask_restful import reqparse, abort, Api, Resource

BASE_URL = '/text-paper-analysis/api/v1.0/'

SAVE_IMAGE_ROOT_DIR = './images'

app = Flask(__name__)

file_handler = logging.FileHandler('app.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def get_barcodes(img_path):
    img = Image.open(img_path)
    
    result = []
    
    barcodes = pyzbar.decode(img)
    for barcode in barcodes:
        result.append((barcode.data.decode("utf-8"), barcode.rect))

    return result


def compression_files(filenames, zip_filename):
    zip_file = zipfile.ZipFile(zip_filename, 'w')

    for filename in filenames:
        zip_file.write(filename, os.path.basename(filename))

    zip_file.close()


def search_files(directory='.', extension=''):
    filenames = []

    extension = extension.lower()
    for dirpath, dirnames, files in os.walk(directory):
        for name in files:
            if extension and name.lower().endswith(extension):
                filenames.append(os.path.join(dirpath, name))
            elif not extension:
                filenames.append(os.path.join(dirpath, name))

    return filenames


def get_image_ratio(img, ref_width, ref_height):
    return (ref_width/img.width, ref_height/img.height)


def image_resize(img, width_ratio, height_ratio):
    width = int(img.width*width_ratio)
    height = int(img.height*height_ratio)

    img = img.resize((width, height), Image.ANTIALIAS)
    return img


def image_crop(img, rect, root_dir, filename):
    region = img.crop(rect)
    region.save(os.path.join(root_dir, filename+'.png'))


#images_dir = 'images'
#files = search_files(images_dir, '.png')
#compression_files(files, 'images/images.zip')

def error_json(message='参数无效', code=400):
    return jsonify({'code': code, 'message': message})


"""
输入：条形码图片
输出：条形码文本
"""
@app.route(BASE_URL + 'barcode_text', methods=['POST'])
def barcode_text():
    barcode = request.files.get('barcode')
    if not barcode:
        return error_json('参数 barcode 没有设置。', code=417), 417

    app.logger.info('Barcode Image Filename: %s' % barcode.filename)

    result = {}
    
    with tempfile.NamedTemporaryFile() as barcode_file:
        img_data = barcode.read()
        barcode_file.write(img_data)
        
        # 获得条形码
        barcodes = get_barcodes(barcode_file)
        if not len(barcodes):
            return error_json('没有找到条形码。', code=417), 417
        
        text = barcodes[0][0]
        rect = barcodes[0][1]

        app.logger.info('Barcode Text {} {}'.format(text, rect))
        
        result['barcode-text'] = text

    return jsonify(result), 201

#"""
#输入：图片、保存的目录名（相对路径，支持多级目录）、参考模板尺寸、相对参考模板的一组矩形尺寸及名字。
#输出：一组矩形尺寸的图片（保存目录名＋矩形尺寸名）。
#"""
#@app.route(BASE_URL + 'analysis', methods=['POST'])
#def analysis():
#    text_paper = request.files.get('text_paper')
#    if not text_paper:
#        return error_json('试卷参数 text_paper 没有设置。', code=417), 417
#
#    app.logger.info('Text Paper Filename: %s' % text_paper.filename)
#    template_width = request.values.get('template_width', 0, type=int)
#    template_height = request.values.get('template_height', 0, type=int)
#    if template_width<=0 or template_height<=0:
#        return error_json('模板尺寸参数（template_width, template_height）不能小于0。', code=417), 417
#
#    save_dir = request.values.get('save_dir', '')
#    if not save_dir:
#        return error_json('保存目录参数 save_dir 没有设置。', code=417), 417
#
#    objects = request.values.getlist('objects')
#    if not objects:
#        return error_json('裁剪对象参数 objects 没有值。', code=417), 417
#
#    save_dir = os.path.join(SAVE_IMAGE_ROOT_DIR, save_dir)
#    if not os.path.exists(save_dir):
#        os.makedirs(save_dir)
#
#
##    print('=========================')
##    print(template_width)
##    print(template_height)
##    print(objects)
##    print('=========================')
#
#    with tempfile.NamedTemporaryFile() as text_paper_file:
#        img_data = text_paper.read()
#        text_paper_file.write(img_data)
#
#        # 获得二维码
#        barcodes = get_barcodes(text_paper_file)
#        test_paper_actual_rect = None
#        if len(barcodes) != 2:
#            return error_json('二维码和条形码数量不对，找到%d个。' % len(barcodes), code=417), 417
#
#        text1 = barcodes[0][0]
#        rect1 = barcodes[0][1]
#        text2 = barcodes[1][0]
#        rect2 = barcodes[1][1]
#
#        app.logger.info('QR code 1 Text {} {}'.format(text1, rect1))
#        app.logger.info('QR code 2 Text {} {}'.format(text2, rect2))
#
#        test_paper_actual_rect = (rect1.left, rect1.top, rect2.left+rect2.width, rect2.top+rect2.height)
#
#        # 根据二维码的位置裁剪出试卷
#        img = Image.open(text_paper_file)
#        region = img.crop(test_paper_actual_rect)
#        #region.save(img_crop_path)
#
#        # 将试卷缩放到模板的尺寸
#        region = image_resize(region, *get_image_ratio(region, template_width, template_height))
#
#        # 将每一道题保存为图片
#        for object in objects:
#            obj = eval(object)
#            image_crop(region, (obj['left'], obj['top'], obj['right'], obj['bottom']), save_dir, obj['name'])
#
#    return jsonify({'status': 'OK'}), 201


"""
输入：图片、保存的目录名（相对路径，支持多级目录）、参考模板尺寸、相对参考模板的一组矩形尺寸及名字。
输出：一组矩形尺寸的图片（保存目录名＋矩形尺寸名）。
"""
@app.route(BASE_URL + 'analysis', methods=['POST'])
def analysis():
    text_paper_filename = request.values.get('text_paper_filename', '')
    if not text_paper_filename:
        return error_json('试卷图片文件名参数 text_paper_filename 没有设置。', code=417), 417

    text_paper_filename = os.path.join(SAVE_IMAGE_ROOT_DIR, text_paper_filename)
    if not os.path.exists(text_paper_filename):
        return error_json('试卷图片文件名 %s 不存在。' % text_paper_filename, code=417), 417

    app.logger.info('Text Paper Filename: %s' % text_paper_filename)
    template_width = request.values.get('template_width', 0, type=int)
    template_height = request.values.get('template_height', 0, type=int)
    if template_width<=0 or template_height<=0:
        return error_json('模板尺寸参数（template_width, template_height）不能小于0。', code=417), 417
    
    save_dir = request.values.get('save_dir', '')
    if not save_dir:
        return error_json('保存目录参数 save_dir 没有设置。', code=417), 417

    objects = request.values.getlist('objects')
    print('>>>>>>', objects)
    if not objects:
        return error_json('裁剪对象参数 objects 没有值。', code=417), 417

    save_dir = os.path.join(SAVE_IMAGE_ROOT_DIR, save_dir)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    
    # 获得二维码
    barcodes = get_barcodes(text_paper_filename)
    test_paper_actual_rect = None
    if len(barcodes) != 2:
        return error_json('二维码和条形码数量不对，找到%d个。' % len(barcodes), code=417), 417
    
    text1 = barcodes[0][0]
    rect1 = barcodes[0][1]
    text2 = barcodes[1][0]
    rect2 = barcodes[1][1]

    app.logger.info('QR code 1 Text {} {}'.format(text1, rect1))
    app.logger.info('QR code 2 Text {} {}'.format(text2, rect2))

    test_paper_actual_rect = (rect1.left, rect1.top, rect2.left+rect2.width, rect2.top+rect2.height)
    
    # 根据二维码的位置裁剪出试卷
    img = Image.open(text_paper_filename)
    region = img.crop(test_paper_actual_rect)

    # 将试卷缩放到模板的尺寸
    region = image_resize(region, *get_image_ratio(region, template_width, template_height))

    # 将每一道题保存为图片
    for object in objects:
        print('>>>>>>', object)
        obj = eval(object)
        image_crop(region, (obj['left'], obj['top'], obj['right'], obj['bottom']), save_dir, obj['name'])


    return jsonify({'status': 'OK'}), 201


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

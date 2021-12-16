import fitz
from fitz.fitz import Link, Pixmap
import math
from PIL import Image, ImageDraw
import sys
import time

'''
将PDF转化为图片
pdfPath pdf文件的路径
imgPath 图像要保存的文件夹
zoom_x x方向的缩放系数
zoom_y y方向的缩放系数
rotation_angle 旋转角度
'''
def pdf_image(pdfPath, imgPath, zoom_x=5, zoom_y=5, rotation_angle=0):
    pdf_png_pages = list()
    # 打开PDF文件
    pdf = fitz.open(pdfPath)
    # 逐页读取PDF
    for pg in range(0, pdf.pageCount):
        print('\r'*100 + f'（阶段1/3）第{pg+1}页转图像，共{pdf.pageCount}页...', end='')
        page = pdf[pg]
        # 设置缩放和旋转系数
        trans = fitz.Matrix(zoom_x, zoom_y).prerotate(rotation_angle)
        pm = page.get_pixmap(matrix=trans, alpha=False)
        # 开始写图像
        pdf_png_pages.append(pm.tobytes(output='png'))
    pdf.close()
    print('\r'*100 + f'（阶段1/3）图像转换完成。')
    return pdf_png_pages

'''
将多个图像合并到一页
images bytes类型的图像列表
page_number 一页上放几个图像
'''
def images_merge(images, images_number_in_one=2, blank_edge_pixels=60, LINE_PIXEL=3):
    import io
    pages_number = math.ceil(len(images) / images_number_in_one) # 合并后的总页数
    pages_images = list() # 所有合并后的页面
    for page_index in range(pages_number):
        single_image_size = Image.open(io.BytesIO(images[page_index])).size # 获取图片尺寸
        print('\r'*100 + f'（阶段2/3）第{page_index+1}页合并图像，共{pages_number}页...', end='')
        # 新建空画布
        pages_images.append(Image.new('RGB', (
            single_image_size[0] * images_number_in_one + blank_edge_pixels*(images_number_in_one + 1), 
            single_image_size[1] + blank_edge_pixels*2), color='White')
        )
        for little_page_index in range(images_number_in_one):
            # 检测最后一页，如果超范围就跳出
            if page_index * images_number_in_one + little_page_index >= len(images):
                break

            # 打开图像
            im = Image.open(io.BytesIO(images[page_index * images_number_in_one + little_page_index]))
            # 在图像四周绘制边框
            if LINE_PIXEL:
                ImageDraw.Draw(im).line(
                    [
                        (0+LINE_PIXEL, 0+LINE_PIXEL), (single_image_size[0]-LINE_PIXEL, 0+LINE_PIXEL),
                        (0+LINE_PIXEL, 0+LINE_PIXEL), (0+LINE_PIXEL, single_image_size[1]-LINE_PIXEL),
                        (0+LINE_PIXEL, single_image_size[1]-LINE_PIXEL), (single_image_size[0]-LINE_PIXEL, single_image_size[1]-LINE_PIXEL),
                        (single_image_size[0]-LINE_PIXEL, single_image_size[1]-LINE_PIXEL), (single_image_size[0]-LINE_PIXEL, 0+LINE_PIXEL)
                    ],
                    fill='Black', width=LINE_PIXEL
                    )
            # 图像放到空画布中
            pages_images[page_index].paste(im, (
                blank_edge_pixels*(little_page_index+1) + single_image_size[0]*little_page_index, 
                blank_edge_pixels, 
                blank_edge_pixels*(little_page_index+1) + single_image_size[0]*(little_page_index+1), 
                blank_edge_pixels+single_image_size[1]
                ))
        #pages_images[page_index].show()
    print('\r'*100 + f'（阶段2/3）图像合并完成。')
    return pages_images

if __name__ == '__main__':
    try:
        import easygui
        if len(sys.argv) == 2:
            path = sys.argv[1]
        elif len(sys.argv) == 1:
            easygui.msgbox(msg='需要通过拖动传入PDF文件！', title='无法继续', ok_button='好嘞')
            sys.exit(1)
        else:
            raise Exception('传入参数的个数不正确。')

        print('1. 1页1图 2. 1页2图 3. 自定义')
        choise = input('请选择：')
        if choise == '1':
            result = [1, 0, 0, 5, 'jpg']
        elif choise == '2':
            result = [2, 60, 3, 5, 'jpg']
        else:
            result = easygui.multenterbox(
                msg='填写以下转换参数。', 
                title='需要参数', 
                fields=['一张图放几页', '边缘留白像素', '外加边框像素', '放大倍率', '图片格式'],
                values=[2, 60, 3, 5, 'jpg']
                )

        # 取出传入参数
        one_page_images_number = int(result[0])
        blank_edge_pixels = int(result[1])
        line_pixel = int(result[2])
        zoom_xy = int(result[3])
        pic_format = result[4]

        pdf_png_pages = pdf_image(path, path, zoom_x=zoom_xy, zoom_y=zoom_xy)
        pages = images_merge(pdf_png_pages, one_page_images_number, blank_edge_pixels, line_pixel)
        print('（阶段3/3）写出文件：')
        for page_index in range(len(pages)):
            print(f'{path}{page_index+1}.{pic_format}')
            pages[page_index].save(f'{path}{page_index+1}.{pic_format}')
        
        # 倒计时退出
        for i in range(3):
            print('\r' * len(f'已完成，{3-i}s 后关闭') + f'已完成，{3-i}s 后关闭', end='')
            time.sleep(1)
    except Exception as e:
        input(f"程序出了些错误！\n出错信息：{e}")
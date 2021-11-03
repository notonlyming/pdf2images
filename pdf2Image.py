import fitz
from fitz.fitz import Link, Pixmap
import math
from PIL import Image, ImageDraw
import sys

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
        print(f'第{pg+1}页转图像，共{pdf.pageCount}页...')
        page = pdf[pg]
        # 设置缩放和旋转系数
        trans = fitz.Matrix(zoom_x, zoom_y).prerotate(rotation_angle)
        pm = page.get_pixmap(matrix=trans, alpha=False)
        # 开始写图像
        pdf_png_pages.append(pm.tobytes(output='png'))
    pdf.close()
    return pdf_png_pages

'''
将多个图像合并到一页
images bytes类型的图像列表
page_number 一页上放几个图像
'''
def images_merge(images, images_number_in_one=2):
    import io
    ONE_CM_PIXEL = 60 # 72像素每英寸下一厘米的近似像素值
    LINE_PIXEL = 3 # 细线边框的厚度
    pages_number = math.ceil(len(images) / images_number_in_one) # 合并后的总页数
    pages_images = list() # 所有合并后的页面
    single_image_size = Image.open(io.BytesIO(images[0])).size # 临时打开第一个图像获取尺寸
    for page_index in range(pages_number):
        print(f'第{page_index+1}页合并图像，共{pages_number}页...')
        # 新建空画布
        pages_images.append(Image.new('RGB', (
            single_image_size[0] * images_number_in_one + ONE_CM_PIXEL*(images_number_in_one + 1), 
            single_image_size[1] + ONE_CM_PIXEL*2), color='White')
        )
        for little_page_index in range(images_number_in_one):
            # 检测最后一页，如果超范围就跳出
            if page_index * images_number_in_one + little_page_index >= len(images):
                break

            # 打开图像
            im = Image.open(io.BytesIO(images[page_index * images_number_in_one + little_page_index]))
            # 在图像四周绘制边框
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
                ONE_CM_PIXEL*(little_page_index+1) + single_image_size[0]*little_page_index, 
                ONE_CM_PIXEL, 
                ONE_CM_PIXEL*(little_page_index+1) + single_image_size[0]*(little_page_index+1), 
                ONE_CM_PIXEL+single_image_size[1]
                ))
        #pages_images[page_index].show()
    return pages_images

if __name__ == '__main__':
    path = sys.argv[1]
    if len(sys.argv) > 2:
        one_page_images_number = int(sys.argv[2])
    else:
        one_page_images_number = 2

    pdf_png_pages = pdf_image(path, path)
    pages = images_merge(pdf_png_pages, one_page_images_number)
    print('写出文件：')
    for page_index in range(len(pages)):
        print(f'{path}{page_index+1}.png')
        pages[page_index].save(f'{path}{page_index+1}.png')
    input('已完成！')

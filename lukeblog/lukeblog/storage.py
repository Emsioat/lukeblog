""" 关于文件上传,储存于服务器的相关配置 """

from io import BytesIO

from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image, ImageDraw, ImageFont


class WatermarkStorage(FileSystemStorage):
    """ 上传保存图片时添加水印 """
    def save(self, name, content, max_length=None):
        """ 重写save,可以在文件上传保存前进行一些操作(如存储在CDN上等） """
        # 为图像加水印
        if 'image' in content.content_type:
            image = self.watermark_with_text(content, '@LukeBlog', 'red')
            content = self.convert_image_to_file(image, name)

        return super().save(name, content, max_length=max_length)

    def convert_image_to_file(self, image, name):
        """ 将最终打上水印的图片对象Image转换为文件对象(即转换为BytesIO对象) """
        temp = BytesIO()
        image.save(temp, format='PNG')
        file_size = temp.tell()
        return InMemoryUploadedFile(temp, None, name, 'image/png', file_size, None)

    def watermark_with_text(self, file_obj, text, color, fontfamily='Arial.ttf'):
        """ 将上传的文件打上水印,并返回图片,fontfamily可以指定本地字体文件路径 """
        image = Image.open(file_obj).convert('RGBA')  # 打开上传的文件,并转换为RGBA的图像
        draw = ImageDraw.Draw(image)  # 将图像创建为可以"画"的对象
        width, height = image.size  # 图像的宽和高
        margin = 10
        if fontfamily:
            font = ImageFont.truetype(fontfamily, int(height / 20))
        else:
            font = None
        textWidth, textHeight = draw.textsize(text, font)
        x = (width - textWidth - margin) / 2  # 计算横轴位置
        y = height - textHeight - margin  # 计算纵轴位置
        draw.text((x, y), text, color, font)
        return image

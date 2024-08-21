# -*- coding: utf-8 -*-
# Name：孙圣雷
# Time：2024/8/6 下午2:14
import fitz
from PIL import Image
import io

def analyse_pdf(pdf_file):
    # TODO analyse_img
    # TODO analyse_text
    pass

def analyse_pdf_img(pdf_file):
    images_list = []
    doc = fitz.open(pdf_file)

    for page_number in range(len(doc)):
        page = doc[page_number]
        images = page.get_images(full=True)
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            images_list.append(image_bytes)
            print(f"提取图像：页面 {page_number + 1}, 图像 {img_index + 1}")

            image = Image.open(io.BytesIO(image_bytes))
            image.show()

    print("所有图像提取完成!")
    return images_list


if __name__ == "__main__":
    analyse_pdf_img("uploads/能源城市报告.pdf")
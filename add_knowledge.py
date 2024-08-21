# -*- coding: utf-8 -*-
# Name：孙圣雷
# Time：2024/8/4 下午5:29
import os
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
""" V2.1 🐳🐳🐳"""
def _add_knowledge(base_url):
    num_pages = 4
    all_news = []
    output_folder = "news"

    os.makedirs(output_folder, exist_ok=True)

    for page in range(1, num_pages + 1):
        url = f"{base_url}_{page}.htm" if page > 1 else f"{base_url}.htm"

        response = requests.get(url)

        if response.status_code == 200:
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = soup.find_all('ul', class_='list')

            for ul in news_items:
                for li in ul.find_all('li'):
                    title_tag = li.find('a')
                    date_tag = li.find('span', class_='data')

                    title = title_tag.text.strip() if title_tag else '无标题'
                    link = title_tag['href'] if title_tag else '无链接'
                    date = date_tag.text.strip() if date_tag else '无日期'

                    if link and link.startswith('/'):
                        link = "http://www.nea.gov.cn" + link

                    all_news.append({'title': title, 'link': link, 'date': date})

        else:
            print(f"请求失败，状态码：{response.status_code}，页面：{url}")

    for index, news in enumerate(all_news, start=1):
        link = news['link']
        if link:
            content_response = requests.get(link)
            if content_response.status_code == 200:
                content_response.encoding = 'utf-8'
                soup = BeautifulSoup(content_response.text, 'html.parser')
                content_td = soup.find('td', align='left', valign='top')

                if content_td:
                    paragraphs = content_td.find_all('p')
                    content = "\n".join([p.get_text(strip=True) for p in paragraphs])

                    pdf_file_path = os.path.join(output_folder, f"{index}.pdf")

                    pdf = FPDF()
                    pdf.add_page()

                    pdf.add_font('SimHei', '', 'simhei.ttf', uni=True)
                    pdf.set_font("SimHei", size=12)

                    pdf.multi_cell(0, 10, f"标题: {news['title']}")
                    pdf.multi_cell(0, 10, f"链接: {news['link']}")
                    pdf.multi_cell(0, 10, f"日期: {news['date']}")
                    pdf.ln(10)
                    pdf.multi_cell(0, 10, content)

                    pdf.output(pdf_file_path)
                    print(f"保存文件: {pdf_file_path}")

                else:
                    print("未找到内容区域。")
            else:
                print(f"请求失败，状态码：{content_response.status_code}，链接：{link}")

    for news in all_news:
        print(f"标题: {news['title']}")
        print(f"链接: {news['link']}")
        print(f"日期: {news['date']}")
        print("---")


""" V2.0 (.txt文档加入知识库不被分割)🐳🐳🐳"""
"""
    def _add_knowledge(base_url):
    num_pages = 10

    all_news = []

    output_folder = "news"
    os.makedirs(output_folder, exist_ok=True)

    for page in range(1, num_pages + 1):
        url = f"{base_url}_{page}.htm" if page > 1 else f"{base_url}.htm"

        response = requests.get(url)

        if response.status_code == 200:
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = soup.find_all('ul', class_='list')

            for ul in news_items:
                for li in ul.find_all('li'):
                    title_tag = li.find('a')
                    date_tag = li.find('span', class_='data')

                    title = title_tag.text.strip() if title_tag else '无标题'
                    link = title_tag['href'] if title_tag else '无链接'
                    date = date_tag.text.strip() if date_tag else '无日期'

                    if link and link.startswith('/'):
                        link = "http://www.nea.gov.cn" + link

                    all_news.append({'title': title, 'link': link, 'date': date})

        else:
            print(f"请求失败，状态码：{response.status_code}，页面：{url}")

    for index, news in enumerate(all_news, start=1):
        link = news['link']
        if link:
            content_response = requests.get(link)
            if content_response.status_code == 200:
                content_response.encoding = 'utf-8'
                soup = BeautifulSoup(content_response.text, 'html.parser')
                content_td = soup.find('td', align='left', valign='top')

                if content_td:
                    paragraphs = content_td.find_all('p')
                    content = "\n".join([p.get_text(strip=True) for p in paragraphs])

                    txt_file_path = os.path.join(output_folder, f"{index}.txt")

                    with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
                        txt_file.write(f"标题: {news['title']}\n")
                        txt_file.write(f"链接: {news['link']}\n")
                        txt_file.write(f"日期: {news['date']}\n\n")
                        txt_file.write(content)

                    print(f"保存文件: {txt_file_path}")
                else:
                    print("未找到内容区域。")
            else:
                print(f"请求失败，状态码：{content_response.status_code}，链接：{link}")

    for news in all_news:
        print(f"标题: {news['title']}")
        print(f"链接: {news['link']}")
        print(f"日期: {news['date']}")
        print("---")
"""

if __name__ == '__main__':
    _add_knowledge("http://www.nea.gov.cn/xwzx/nyyw")

""" V1.1 """
# def _add_knowledge(base_url, db_name):
#     num_pages = 10
#     output_folder = "news_txts"
#     os.makedirs(output_folder, exist_ok=True)
#
#     for page in range(1, num_pages + 1):
#         url = f"{base_url}_{page}.htm" if page > 1 else f"{base_url}.htm"
#
#         response = requests.get(url)
#
#         if response.status_code == 200:
#             response.encoding = 'utf-8'
#             soup = BeautifulSoup(response.text, 'html.parser')
#             news_items = soup.find_all('ul', class_='list')
#
#             all_news = []
#
#             for ul in news_items:
#                 for li in ul.find_all('li'):
#                     title_tag = li.find('a')
#                     date_tag = li.find('span', class_='data')
#
#                     title = title_tag.text.strip() if title_tag else '无标题'
#                     link = title_tag['href'] if title_tag else '无链接'
#                     date = date_tag.text.strip() if date_tag else '无日期'
#
#                     if link and link.startswith('/'):
#                         link = "http://www.nea.gov.cn" + link
#
#                     all_news.append({'title': title, 'link': link, 'date': date})
#
#             for index, news in enumerate(all_news, start=1):
#                 link = news['link']
#                 if link:
#                     content_response = requests.get(link)
#                     if content_response.status_code == 200:
#                         content_response.encoding = 'utf-8'
#                         soup = BeautifulSoup(content_response.text, 'html.parser')
#                         content_td = soup.find('td', align='left', valign='top')
#
#                         if content_td:
#                             paragraphs = content_td.find_all('p')
#                             content = "\n".join([p.get_text(strip=True) for p in paragraphs])
#
#                             txt_file_path = os.path.join(output_folder, f"{index}.txt")
#
#                             with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
#                                 txt_file.write(f"标题: {news['title']}\n")
#                                 txt_file.write(f"链接: {news['link']}\n")
#                                 txt_file.write(f"日期: {news['date']}\n\n")
#                                 txt_file.write(content)
#
#                             print(f"保存文件: {txt_file_path}")
#
#                             print("step1"+link+"\n")
#                             add_chroma_db(db_name, content, link)
#
#                         else:
#                             print("未找到内容区域。")
#                     else:
#                         print(f"请求失败，状态码：{content_response.status_code}，链接：{link}")
#
#         else:
#             print(f"请求失败，状态码：{response.status_code}，页面：{url}")
#
#     for news in all_news:
#         print(f"标题: {news['title']}")
#         print(f"链接: {news['link']}")
#         print(f"日期: {news['date']}")
#         print("---")
#



""" V1.0 """
# def _add_knowledge(base_url):
#     num_pages = 10
#
#     # base_url = "http://www.nea.gov.cn/xwzx/nyyw"
#
#     all_news = []
#
#     output_folder = "news_txts"
#     os.makedirs(output_folder, exist_ok=True)
#
#     for page in range(1, num_pages + 1):
#         url = f"{base_url}_{page}.htm" if page > 1 else f"{base_url}.htm"
#
#         response = requests.get(url)
#
#         if response.status_code == 200:
#             response.encoding = 'utf-8'
#             soup = BeautifulSoup(response.text, 'html.parser')
#             news_items = soup.find_all('ul', class_='list')
#
#             for ul in news_items:
#                 for li in ul.find_all('li'):
#                     title_tag = li.find('a')
#                     date_tag = li.find('span', class_='data')
#
#                     title = title_tag.text.strip() if title_tag else '无标题'
#                     link = title_tag['href'] if title_tag else '无链接'
#                     date = date_tag.text.strip() if date_tag else '无日期'
#
#                     if link and link.startswith('/'):
#                         link = "http://www.nea.gov.cn" + link
#
#                     all_news.append({'title': title, 'link': link, 'date': date})
#
#         else:
#             print(f"请求失败，状态码：{response.status_code}，页面：{url}")
#
#     for index, news in enumerate(all_news, start=1):
#         link = news['link']
#         if link:
#             content_response = requests.get(link)
#             if content_response.status_code == 200:
#                 content_response.encoding = 'utf-8'
#                 soup = BeautifulSoup(content_response.text, 'html.parser')
#                 content_td = soup.find('td', align='left', valign='top')
#
#                 if content_td:
#                     paragraphs = content_td.find_all('p')
#                     content = "\n".join([p.get_text(strip=True) for p in paragraphs])
#
#                     txt_file_path = os.path.join(output_folder, f"{index}.txt")
#
#                     with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
#                         txt_file.write(f"标题: {news['title']}\n")
#                         txt_file.write(f"链接: {news['link']}\n")
#                         txt_file.write(f"日期: {news['date']}\n\n")
#                         txt_file.write(content)
#
#                     print(f"保存文件: {txt_file_path}")
#                 else:
#                     print("未找到内容区域。")
#             else:
#                 print(f"请求失败，状态码：{content_response.status_code}，链接：{link}")
#
#     for news in all_news:
#         print(f"标题: {news['title']}")
#         print(f"链接: {news['link']}")
#         print(f"日期: {news['date']}")
#         print("---")






# if __name__ == '__main__':
#     add_knowledge("http://www.nea.gov.cn/xwzx/nyyw")

# import requests
# from bs4 import BeautifulSoup
#
# num_pages = 10
#
# base_url = "http://www.nea.gov.cn/xwzx/nyyw"
#
# all_news = []
#
# for page in range(1, num_pages + 1):
#     url = f"{base_url}_{page}.htm" if page > 1 else f"{base_url}.htm"
#
#     response = requests.get(url)
#
#     if response.status_code == 200:
#         response.encoding = 'utf-8'
#
#         soup = BeautifulSoup(response.text, 'html.parser')
#
#         news_items = soup.find_all('ul', class_='list')
#
#         for ul in news_items:
#             for li in ul.find_all('li'):
#                 title_tag = li.find('a')
#                 date_tag = li.find('span', class_='data')
#
#                 title = title_tag.text.strip() if title_tag else '无标题'
#                 link = title_tag['href'] if title_tag else '无链接'
#                 date = date_tag.text.strip() if date_tag else '无日期'
#
#                 if link and link.startswith('/'):
#                     link = "http://www.nea.gov.cn" + link
#
#                 all_news.append({'title': title, 'link': link, 'date': date})
#
#     else:
#         print(f"请求失败，状态码：{response.status_code}，页面：{url}")
#
# for news in all_news:
#     link = news['link']
#     if link:
#         content_response = requests.get(link)
#         if content_response.status_code == 200:
#             content_response.encoding = 'utf-8'
#             soup = BeautifulSoup(content_response.text, 'html.parser')
#
#             content_td = soup.find('td', align='left', valign='top')
#
#             if content_td:
#                 paragraphs = content_td.find_all('p')
#                 content = "\n".join([p.get_text(strip=True) for p in paragraphs])
#                 news['content'] = content  # 将内容存储在当前新闻字典中
#             else:
#                 news['content'] = "未找到内容区域。"
#         else:
#             news['content'] = f"请求失败，状态码：{content_response.status_code}，链接：{link}"
#
# for news in all_news:
#     print(f"标题: {news['title']}")
#     print(f"链接: {news['link']}")
#     print(f"日期: {news['date']}")
#     print(f"内容: {news.get('content', '')[:100]}...")
#     print("---")

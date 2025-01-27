import requests
import json

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

class TextinOcr(object):
    def __init__(self, app_id, app_secret):
        self._app_id = app_id
        self._app_secret = app_secret
        self.host = 'https://api.textin.com'

    def recognize_pdf2md(self, image_path, options, is_url=False):
        """
        pdf to markdown
        :param options: request params
        :param image_path: string
        :param is_url: bool
        :return: response

        options = {
            'pdf_pwd': None,
            'dpi': 144,  # 设置 dpi 为 144
            'page_start': 0,
            'page_count': 1000,  # 设置解析的页数为 1000 页
            'apply_document_tree': 0,
            'markdown_details': 1,
            'page_details': 0,  # 不包含页面细节信息
            'table_flavor': 'md',
            'get_image': 'none',
            'parse_mode': 'scan',  # 解析模式设为 scan
        }
        """
        url = self.host + '/ai/service/v1/pdf_to_markdown'
        headers = {
            'x-ti-app-id': self._app_id,
            'x-ti-secret-code': self._app_secret
        }
        if is_url:
            image = image_path
            headers['Content-Type'] = 'text/plain'
        else:
            image = get_file_content(image_path)
            headers['Content-Type'] = 'application/octet-stream'

        return requests.post(url, data=image, headers=headers, params=options)


if __name__ == "__main__":
    # 请登录后前往“工作台 - 账号设置 - 开发者信息”查看 app-id/app-secret
    textin = TextinOcr('a99549228f8cf09028d83027422beae2', '54fe2e9e9b2c24e1b8c1af85f6df6f75')

    # 示例 1：传输文件
    image = 'README.pdf'
    resp = textin.recognize_pdf2md(image, {
        'page_start': 0,
        'page_count': 1000,  # 设置解析页数为 1000 页
        'table_flavor': 'md',
        'parse_mode': 'scan',  # 设置解析模式为 scan 模式
        'page_details': 0,  # 不包含页面细节
        'markdown_details': 1,
        'apply_document_tree': 1,
        'dpi': 144  # 分辨率设置为 144 dpi
    })
    print("request time: ", resp.elapsed.total_seconds())

    result = json.loads(resp.text)
    with open('result_1.json', 'w', encoding='utf-8') as fw:
        json.dump(result, fw, indent=4, ensure_ascii=False)

    # 示例 2：传输 URL
    image = 'https://example.com/example.pdf'
    resp = textin.recognize_pdf2md(image, {
        'page_start': 0,
        'page_count': 1000,  # 设置解析页数为 1000 页
        'table_flavor': 'md',
        'parse_mode': 'scan',  # 设置解析模式为 scan 模式
        'page_details': 0,  # 不包含页面细节
        'markdown_details': 1,
        'apply_document_tree': 1,
        'dpi': 144  # 分辨率设置为 144 dpi
    }, True)
    print("request time: ", resp.elapsed.total_seconds())

    result = json.loads(resp.text)
    with open('result_2.json', 'w', encoding='utf-8') as fw:
        json.dump(result, fw, indent=4, ensure_ascii=False)

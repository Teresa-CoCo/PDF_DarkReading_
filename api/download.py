def do_GET(self):
        # 解析URL
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/download':
            # 处理下载请求
            query = parse_qs(parsed_path.query)
            if 'file' in query:
                filename = query['file'][0]
                try:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/pdf')
                    self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(filename)}"')
                    self.end_headers()
                    with open(filename, 'rb') as file:
                        self.wfile.write(file.read())
                    # 清理文件
                    os.remove(filename)
                    return
                except Exception as e:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"File not found.")
                    return
        # 默认显示上传表单
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'''
            <html>
            <head>
                <title>Upload PDF for Night Mode Conversion</title>
            </head>
            <body>
                <form enctype="multipart/form-data" method="post">
                    <input name="file" type="file" />
                    <input type="submit" value="Upload" />
                </form>
            </body>
            </html>
        ''')

def handler(request):
    # 这里使用request数据来处理上传逻辑
    # 返回相应的响应对象
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": "处理上传逻辑并返回结果"
    }
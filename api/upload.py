def do_POST(self):
        form = FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })

        fileitem = form['file']
        if fileitem.filename:
            fn = os.path.basename(fileitem.filename)
            with tempfile.NamedTemporaryFile(delete=False) as temp_pdf, \
                 tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as output_pdf:
                temp_pdf.write(fileitem.file.read())
                temp_pdf_path = temp_pdf.name
                output_pdf_path = output_pdf.name

                # Process PDF
                process_pdf_night_mode(temp_pdf_path, output_pdf_path)
                
                # 提供下载的HTML链接
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                download_link = f'/download?file={output_pdf_path}'
                self.wfile.write(f'<html><body>Processed PDF ready. <a href="{download_link}">Download</a></body></html>'.encode())
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"File is missing")
def handler(request):
    # 这里使用request数据来处理上传逻辑
    # 返回相应的响应对象
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": "处理上传逻辑并返回结果"
    }



from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from socketserver import ThreadingMixIn
import threading
from urllib.parse import urlparse, parse_qs
from cgi import FieldStorage
import tempfile
from pdf2image import convert_from_path
from PIL import Image, ImageOps
import numpy as np
import gc
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True  
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

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
            <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload PDF for Night Mode Conversion</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
            font-size: 24px;
            text-align: center;
        }
        form {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        input[type="file"] {
            border: 1px solid #ccc;
            display: block;
            padding: 6px;
        }
        input[type="submit"] {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 4px;
            transition: background-color 0.3s ease;
        }
        input[type="submit"]:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Upload PDF for Night Mode Conversion</h1>
        <form enctype="multipart/form-data" method="post">
            <input name="file" type="file" />
            <input type="submit" value="Upload" />
        </form>
    </div>
</body>
</html>

        ''')

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

from PyPDF2 import PdfFileReader, PdfFileWriter
chunk_size = 200
def split_pdf(filepath, chunk_size):
    pdf = PdfFileReader(filepath)
    total_pages = pdf.getNumPages()
    print(total_pages)

    for i in range(0, total_pages, chunk_size):
        pdf_writer = PdfFileWriter()
        for j in range(i, min(i + chunk_size, total_pages)):
            pdf_writer.addPage(pdf.getPage(j))

        output_filename = f'{filepath}_{i//chunk_size}.pdf'

        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)

        print(f'Created: {output_filename}')
    
    return total_pages

def process_chunk(filepath):
    images = convert_from_path(filepath)
    processed_images = []
    for img in images:
        img_gray = img.convert("L")
        img_inverted = ImageOps.invert(img_gray)
        data = np.array(img_inverted)
        
        low_gray_mask = data < 31
        data[low_gray_mask] = 31
        high_gray_mask = data >= 200
        data[high_gray_mask] = 240
        
        img_modified = Image.fromarray(data)
        processed_images.append(img_modified)
    
    return processed_images

def merge_images(images, output_path):
    images[0].save(output_path, save_all=True, append_images=images[1:])

def process_pdf_night_mode(filepath, output_path):
    # Split the PDF into chunks
    total_pages = split_pdf(filepath, chunk_size)

    # Process each chunk and collect all processed images
    all_processed_images = []
    for i in range(0, total_pages, chunk_size):
        chunk_filepath = f'{filepath}_{i//chunk_size}.pdf'
        processed_images = process_chunk(chunk_filepath)
        all_processed_images.extend(processed_images)
        print(f'Processed: {chunk_filepath}')

    # Merge all processed images into one PDF
    merge_images(all_processed_images, output_path)

    gc.collect()
# if __name__ == '__main__':
#     from sys import argv
    
#     if len(argv) == 2:
#         run(port=int(argv[1]))
#     else:
#         run()
def run(server_class=ThreadedHTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port} with thread: {threading.currentThread().getName()}')
    httpd.serve_forever()

if __name__ == '__main__':
    from sys import argv
    
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
from socket import *
from select import select
import re

class HTTPServer:
    def __init__(self,host='0.0.0.0',port=80,html=None):
        self.host = host
        self.port = port
        self.html = html
        self.rlist = []
        self.wlist = []
        self.xlist = []
        self.create_socket()
        self.bind()

    def create_socket(self):
        self.sockfd = socket()
        self.sockfd.setblocking(False)

    def bind(self):
        self.addr = (self.host,self.port)
        self.sockfd.bind(self.addr)

    def start(self):
        self.sockfd.listen(3)
        print('Connect from ',self.addr)

        self.rlist.append(self.sockfd)
        while True:
            rs,ws,xs = select(self.rlist, self.wlist, self.xlist)
            for event in rs:
                if event is self.sockfd:
                    c, addr = event.accept()
                    print('connect from', addr)
                    c.setblocking(False)
                    self.rlist.append(c)
                else:
                    self.handle(event)

    def handle(self,connfd):
        request = connfd.recv(1024).decode()
        # print(request)
        pattern = r"[A-Z]+\s+(/\S*)"
        try:
            info = re.match(pattern,request).group(1)
            # print(info)
        except:
            self.rlist.remove(connfd)
            connfd.close()
            return
        else:
            self.get_html(connfd,info)
        # self.response(connfd)

    def get_html(self,connfd,info):
        if info == '/':
            filename = self.html + "/index.html"
        else:
            filename = self.html + info

        try:
            f = open(filename,'rb')
        except:
            response_headers  = "HTTP/1.1 404 NOT FOUND\r\n"
            response_headers += "Content-Type:text/html\r\n"
            response_headers += "\r\n"
            response_content = "<h1>Sorry......</h1>"
            response = (response_headers + response_content).encode()
        else:
            response_content = f.read()
            response_headers = "HTTP/1.1 200 OK\r\n"
            response_headers += "Content-Type:text/html\r\n"
            response_headers += "Content-Length:%d\r\n"%len(response_content)
            response_headers += "\r\n"
            response = response_headers.encode() + response_content
            f.close()
        finally:
            connfd.send(response)

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 8000
    dir = './static'
    httpd = HTTPServer(host=host,port=port,html=dir)
    httpd.start()
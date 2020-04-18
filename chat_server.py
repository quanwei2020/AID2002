"""
chat room
env: python3.6
socket udp  and process
"""
from socket import *
from multiprocessing import Process


# 服务器地址
HOST = "0.0.0.0"
PORT = 8080
ADDR = (HOST,PORT)


# 用户信息存储  {name : address}
user = {}
user_warn_count = {}
user_warn_addr = []
list_warn_word = ['xx','aa','bb','oo']

# 处理进入聊天室
def do_login(s,name,addr):
    if name not in user and '管理' not in name and addr not in user_warn_addr:
        s.sendto(b"ok", addr)
        # 告知其他人
        msg = "\n欢迎 %s 进入聊天室" % name
        for i in user:
            s.sendto(msg.encode(), user[i])
        user[name] = addr# 字典中增加一项
        user_warn_count[name] = 0
    else:
        s.sendto('该用户名已存在，请重新输入'.encode(), addr)
        return

# 处理聊天
def do_chat(s,name,text):
    for word in list_warn_word:
        if word in text:
            text = 'warning:%s聊天内容中包含敏感词汇' % name
            msg = '管理员:' + text
            for i in user:
                s.sendto(msg.encode(), user[i])
            user_warn_count[name] += 1
            if user_warn_count[name] == 3:
                user_warn_addr.append(user[name])
                # msg = "\n你已被踢出聊天室"
                # s.sendto(msg.encode(), user[name])
                del user[name]
                msg = "\n%s 被踢出聊天室" % name
                for i in user:
                    s.sendto(msg.encode(), user[i])
            return
    msg = '\n%s : %s'%(name,text)
    for i in user:
        if i != name:# 除去本人
            s.sendto(msg.encode(), user[i])

# 处理退出
def do_quit(s,name):
    del user[name]
    msg = "\n%s 退出聊天室" % name
    for i in user:
        s.sendto(msg.encode(), user[i])

# 接收各个客户端请求
def request(s):
    """
    总分模式
    1. 接收不同的客户端请求类型
    2. 分情况讨论
    3. 不同的情况调用 不同的封装方法
    4. 每个封装功能设计参考 学的函数或者类的设计过程
    """
    while True:
        data,addr = s.recvfrom(1024)# 接收请求
        tmp = data.decode().split(' ',2)# 对请求解析
        if tmp[0] == 'L':
            # 处理进入聊天室 tmp --> ['L', 'name']
            do_login(s,tmp[1],addr)
        elif tmp[0] == 'C':
            # 处理聊天  tmp --> [C , name,text]
            do_chat(s,tmp[1],tmp[2])
        elif tmp[0] == 'Q':
            # 处理退出 tmp --> [Q,  name]
            do_quit(s,tmp[1])

# 发送管理员消息
def Manager(s):
    while True:
        text = input("管理员发言：")
        msg = 'C 管理员 ' + text
        s.sendto(msg.encode(),ADDR) # 从父进程将消息发送给子进程

# 搭建基本结构
def main():
    # 创建一个udp套接字
    s = socket(AF_INET,SOCK_DGRAM)
    s.bind(ADDR)

    # 创建新的进程用于给客户端发送管理员消息
    p = Process(target=request,args=(s,))
    p.start()
    Manager(s) # 处理发来的请求
    p.join()
    s.close()

if __name__ == '__main__':
    main()
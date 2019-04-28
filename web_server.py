# 访问的相同页面时，页面的内容分为2种方式：
# 1. 静态页面：页面的内容不会变化
# 2. 动态页面：页面的内容会随着实际情况发生变化，例如百度新闻页面，骨架是一样的，但是不一样的时间点访问时获取的页面内容不同

import socket
import re
import multiprocessing
import sys

# 定义一个全局变量，用来存储查找web框架的路径
VIEWS_PATH = "./views"
# 定义一个全局变量，用来存储将来返回给浏览器静态资源文件的路径
STATIC_PATH = "./static"


class Server(object):

    def __init__(self, port, app):
        # 1. 创建套接字
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 为了保证在tcp先断开的情况下，下一次依然能够使用指定的端口，需要设置
        self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 2. 绑定本地信息
        self.tcp_server_socket.bind(("", port))

        # 3. 变成监听套接字
        self.tcp_server_socket.listen(128)

        # 定义2个属性，用来存储web框架传递过来的状态码以及响应头
        self.status = ""  # 指向状态码字符串
        self.headers = None  # 指向一个新的列表

        # 定义一个属性，存储调用web框架时的入口函数
        self.app = app

    def handle_request(self, client_socket):
        """
        处理浏览器发送过来的数据
        然后回送相对应的数据（html、css、js、img。。。）
        :return:
        """
        # 1. 接收
        recv_content = client_socket.recv(1024).decode("utf-8", errors="ignore")

        # print("-----接收到的数据如下----：")
        lines = recv_content.splitlines()  # 将接收到的http的request请求数据按照行进行切割到一个列表中
        # for line in lines:
        #     print("---")

        # 2. 处理请求
        # 提取出浏览器发送过来的request中的路径
        # GET / HTTP/1.1
        # GET /index.html HTTP/1.1

        # 提取出/index.html 或者 /
        try:
            request_file_path = re.match(r"[^/]+(/[^ ]*)", lines[0]).group(1)
        #
        # print("----提出来的请求路径是：----")
        # print(request_file_path)
        except Exception:
            print("未知请求")
        # 完善对方访问主页的情况，如果只有/那么就认为浏览器要访问的是主页
        if request_file_path == "/":
            request_file_path = "/index.html"

        # 如果请求的后缀不是.html结尾，那么就认为是普通的静态资源（就是静态页面）
        if not request_file_path.endswith(".html"):

            try:
                # 从html文件夹中读取出对应的文件的数据内容
                # "." + "/static/css/bootstrap.min.css"
                # ---->./static/css/bootstrap.min.css
                with open(STATIC_PATH + request_file_path, "rb") as f:
                    content = f.read()
            except Exception:
                # 如果要是有异常，那么就认为：找不到那个对应的文件，此时就应该对浏览器404
                pass
                response_headers = "HTTP/1.1 404 Not Found\r\n"
                response_headers += "Content-Type:text/html;charset=utf-8\r\n"
                response_headers += "\r\n"
                response_boy = "----sorry，the file you need not found-------"
                response = response_headers + response_boy
                # 3.2 给浏览器回送对应的数据
                client_socket.send(response.encode("utf-8"))
            else:
                # 如果要是没有异常，那么就认为：找到了指定的文件，将其数据回送给浏览器即可
                response_headers = "HTTP/1.1 200 OK\r\n"
                # response_headers += "Content-Type:text/html;charset=utf-8\r\n"
                response_headers += "\r\n"
                response_boy = content
                response = response_headers.encode("utf-8") + response_boy
                # 3.2 给浏览器回送对应的数据
                client_socket.send(response)
        else:
            print("收到的请求头")
            print(recv_content)
            # 如果是以.html结尾的请求，那么就进行动态生成页面内容

            env = dict()  # 定义个字典，用来封装数据，然后传递到application函数中
            env["PATH_INFO"] = request_file_path  # "/login.py"
            env["MODE"] = "HTTP"
            for i in lines:
                if "Cookie" in i:
                    env["COOKIE"] = i
                    break
            # 如果是 POST 请求
            
            if re.match("POST",lines[0]):
                env["MODE"] = "POST" # 向框架表明是POTS数据
                print(env["MODE"])
                pots = lines[-1]  # 可以取到pots内容
                pots = pots.split("&")  # 切割成 ["xxx=xxx","xxx=xxx"]
                # 这是一个储存 传输内容的字典
                post_dict = dict()
                # 开始添加到新字典
                for i in pots:
                    i = i.split("=")  # i = ["username",["123456"]]
                    post_dict[i[0]] = i[1] # 变成{"username":"123456"}
                env["POST"] = post_dict

            response_boy = self.app(env, self.set_status_headers)

            # 将header和body进行合并成一个整体，作为response的内容
            response_headers = "HTTP/1.1 %s\r\n" % self.status
            for header in self.headers:
                response_headers += "%s:%s\r\n" % (header[0], header[1])
            response_headers += "\r\n"

            response = response_headers + response_boy
            # 3.2 给浏览器回送对应的数据
            client_socket.send(response.encode("utf-8"))

        # 4. 关闭套接字
        client_socket.close()

    def set_status_headers(self, status, headers):
        self.status = status  # "200 OK"
        self.headers = headers  # [("Content-Type", "text/html;charset=utf-8")]

    def run(self):
        """
        用来控制整体
        :return:
        """
        while True:
            # 4. 等待客户端的链接
            client_socket, client_info = self.tcp_server_socket.accept()

            # 5. 为客户端服务
            # handle_request(client_socket)
            p = multiprocessing.Process(target=self.handle_request, args=(client_socket,))
            p.start()

            # 如果是创建了一个子进程去使用client_socket，那么子进程会复制一份这个套接字，所以要在主进程中关闭一次
            # 这样能够保证在子进程接收且调用close时，能够真正的将这个套接字关闭，如果主进程中没有close。那么即使子进程使用了close
            # 这个套接字也不会被真正的关闭，所以就不会有tcp的4次挥手
            #
            # 简单来说：如果是子进程，那么 就要在主进程中关闭一次
            #         如果是子线程，那么 就不要再主进程中关闭，因为线程的方式是共享，而进程的方式是复制
            client_socket.close()

        # 6. 关闭套接字
        self.tcp_server_socket.close()


def main():
    """
    完成整体的控制
    :return:
    """

    # 1. 判断一下运行时参数的个数是否符合要求
    # python3 http_server.py 8081 mini_web:application
    if len(sys.argv) == 3:
        # 2. 提取端口
        port = sys.argv[1]  # "8081"
        if port.isdigit():  # 如果是纯数字的字符串，那么就进行转换
            port = int(port)
        else:
            # 如果不是纯数字的端口号，则停止运行
            exit("端口号需要纯数字...")
    else:
        # 如果运行的参数个数不满足，那么程序退出运行
        exit("运行时参数有误，请按照：python3 xxxx.py port web_framework_name:application 运行")

    # 3. 提取web框架的名字以及入口函数
    framework_app_name = sys.argv[2]  # "mini_web:application"

    # 4. 提取出框架的名字以及应用程序入口的名字
    ret = re.match(r"([^:]+):(.+)", framework_app_name)
    if ret:
        framework_name = ret.group(1)  # "mini_web"
        app_name = ret.group(2)  # "application"
    else:
        # 输入的框架名字以及入口函数名字不符合要求
        exit("输入的框架名字以及入口函数名字不符合要求")

    # 修改sys.path这个导入模块时查找的路径列表
    sys.path.insert(0, VIEWS_PATH)

    # 5. 根据web框架的名字 导入这个.py文件
    # import framework_name  # 这句话不能实现 import mini_web，它会将framework_name当做 要查找的.py名字，
    # 而不是找这个变量中的值 对应的.py名字
    framework = __import__(framework_name)  # framework变量此时指向了刚刚导入的 "mini_web.py"

    # 6. 到导入的模块对象中获取想要的函数引用
    # 因为framework变量此时指向了mini_web.py这个模块，所以当我们是使用getattr(framework, app_name)的时候
    # 就理解为：到mini_web.py中找到app_name这个变量想要的那个名字对应的函数引用，又因为app_name此时是"appliction"
    # 所以最后的结果就理解为：到mini_web.py中找application这个函数，把这个函数的引用返回
    # 最后app变量指向了mini_web.py中的application函数
    app = getattr(framework, app_name)

    # 7. 创建Server服务器对象
    server = Server(port, app)

    # 8. 调用它的运行方法
    server.run()


if __name__ == '__main__':
    main()

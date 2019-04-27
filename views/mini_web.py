import re
import time
import pymysql
from urllib.parse import unquote
from contextlib import contextmanager


# 定义一个字典，用来存储 url以及对应的func 的对应关系，key：url， value：func
URL_ROUTE = dict()
# {
#     r"/update/\d+.html": show_update_page,
# }


# 定义一个全局变量，用来存储 找html页面时的路径
TEMPLATES_PATH = "./templates"


@contextmanager
def mini_open(file_path, model="r"):
    f = open(TEMPLATES_PATH + file_path, model, encoding="utf-8")
    yield f
    f.close()


def route(url):  # "/login.py"
    def set_func(func):  # login函数名
        # 将url与func进行关联，此时就是映射
        URL_ROUTE[url] = func

        def call_func(*args, **kwargs):
            return func(*args, **kwargs)
        return call_func
    return set_func


@route(r"/payply\.html")
def payply():
    """
    提交订单
    :return:
    """
    pass


@route(r"/info\.html")
def info():
    """
    收货地址
    :return:
    """
    # 1. 获取对应的html模板
    with mini_open("/index.html") as f:
        content = f.read()

    # 从MySQL中查询数据
    address = pymysql.connect(host="localhost", port="8080", user="root", password="123456", database="", charset="utf8")
    cursor = address.cursor()
    # sql语句
    sql = "update "
    # 执行sql语句
    cursor.execute(sql)
    data_from_mysql = cursor.fetchall()
    cursor.close()
    address.close()

    # 找到模板
    html_template = """
                    <dd>
                        <div class="item">
                            <span><font>*</font>"所在地区："</span>
                            <select><option>广东省</option></select>
                            <select><option>深圳市</option></select>
                            <input type="tex" class="txt">
                        </div>
                        <div class="item"><span>
                            <font>*</font>"邮政编码："
                        </span>
                            <input type="tex" class="txt">
                        </div>
                        <div class="item"><table width="100%" border="0" cellpadding="0">
                            <tbody><tr>
                                <td width="8%">
                                    <span><font>*</font>"详细地址："</span>
                                </td>
                                <td width="92%"><textarea style="margin: 0px; height: 125px; width: 437px;"></textarea></td>
                            </tr></tbody>
                        </table></div>
                        <div class="item"><span><font>*</font>"收货人姓名："</span>
                            <input type="tex" class="txt">
                        </div>
                        <div class="item"><span><font>*</font>"手机："</span>
                            <input type="tex" class="txt">
                        </div>
                        <div class="item"><span><font>*</font>"电话："
                            <input type="tex class="txt">
                        </span></div>
                        <div class="item"><input type="submit" class="sub" value="保存收货人信息"></div>
                    </dd>
    
    """

    # 3. 替换
    html = ""
    for one_stock_info in data_from_mysql:
        html += html_template.format(one_stock_info)

    # 通过正则表达式替换 html模板中 变量
    content = re.sub(r"\{% content %\}", html, content)

    return content


@route("404")
def page_404():
    return "404，当前时间是：%s" % time.ctime()


@route(r"/index\.html")
def index():

    # 1. 获取对应的html模板
    with mini_open("/index.html") as f:
        content = f.read()


    return content


@route(r"/login\.html")
def login():

    # 1. 获取对应的html模板
    with mini_open("/login.html") as f:
        content = f.read()


    return content

@route(r"/member\.html")
def member():

    # 1. 获取对应的html模板
    with mini_open("/member.html") as f:
        content = f.read()


    return content

@route(r"/shopcar\.html")
def shopcar():

    # 1. 获取对应的html模板
    with mini_open("/shopcar.html") as f:
        content = f.read()


    return content

@route(r"/reg\.html")
def reg():

    # 1. 获取对应的html模板
    with mini_open("/reg.html") as f:
        content = f.read()


    return content

def application(env, call_func):
    """
    接收web服务器传递过来的 请求参数
    :param file_path:
    :return:
    """
    # 2. 根据映射的关系即URL_ROUTE这字典，根据不同的url请求调用对应的函数
    # 2.0 提取url中的路径
    file_path = env["PATH_INFO"]  # "/login.html"

    print("\n\n")
    print("------------1------start---------")
    print(URL_ROUTE)
    print("------------1------stop---------")

    # 2.1 提取函数引用
    for url, func in URL_ROUTE.items():
        # url--->r"/update/\d+.html"
        # func-->show_update_page
        ret = re.match(url, file_path)  # 相当于re.match(r"/update/(\d+)\.html", "/update/300268.html")
        if ret:
            # 如果匹配成功
            # 回调 call_func变量指向的函数，并且将 状态码以及header传递过去
            call_func("200 OK", [("Content-Type", "text/html;charset=utf-8"), ("framework", "mini_web")])

            print("\n\n\n\n")
            print("url:", file_path)
            print(func.__name__)
            print(func.__code__.co_argcount)

            paraments = []  # 用来存储从正则表达式中提取出来的数据
            for i in range(func.__code__.co_argcount):
                paraments.append(ret.group(1+i))

            # 调用函数
            response_body = func(*paraments)  # response_body = login("/login.html")
            break
    else:
        # 没有匹配成功
        # 回调 call_func变量指向的函数，并且将 状态码以及header传递过去
        call_func("404 Not Found", [("Content-Type", "text/html;charset=utf-8"), ("framework", "mini_web")])
        # 如果浏览器请求的url没有在 路由映射字典中找到，那么就返回一个默认的404处理函数
        func = URL_ROUTE.get("404", lambda x: "not found you page ,404")
        response_body = func(file_path)

    # 返回数据给web服务器
    return response_body

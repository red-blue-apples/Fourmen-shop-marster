import re
import time
import pymysql
from urllib.parse import unquote
import requests
from contextlib import contextmanager

# 定义一个字典，用来存储 url以及对应的func 的对应关系，key：url， value：func
URL_ROUTE = dict()
# {
#     r"/update/\d+.html": show_update_page,
# }+-
DATABASE = '192.168.14.53'

# 定义一个全局变量，用来存储 找html页面时的路径
TEMPLATES_PATH = "./templates"


@contextmanager
def mini_open(file_path, model="r"):
    f = open(TEMPLATES_PATH + file_path, model, encoding="utf-8")
    yield f
    f.close()


def redirect(call_func):
    """
    检测没有登录就返回到登录界面
    :return:
    """
    call_func("302 Temporarily Moved",
              [("Content-Type", "text/html;charset=utf-8"), ("framework", "mini_web"), ("Location", "./login.html")])
    return "302"


def route(url):  # "/login.py"
    def set_func(func):  # login函数名
        # 将url与func进行关联，此时就是映射
        URL_ROUTE[url] = func

        def call_func(*args, **kwargs):
            return func(*args, **kwargs)

        return call_func

    return set_func


@route(r"/shopcar\.html")
def shopcar():
    """
    购物车
    :return:
    """
    # 1. 获取对应的html模板
    # with mini_open("/shopcar.html") as f:
    #     content = f.read()
    print("===")
    # 跳转页面
    info()


@route(r"/info\.html")
def info():
    """
    收货地址
    :return:
    """
    # 1. 获取对应的html模板
    with mini_open("/info.html") as f:
        content = f.read()

    # 从MySQL中查询数据





    address = pymysql.connect(host="localhost", port="8080", user="root", password="123456", database="adderss", charset="utf8")

    cursor = address.cursor()
    # sql语句
    sql = """update adderss """
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


@route(r"/payply\.html")
def payply():
    """
    提交订单
    :return:
    """
    pass


@route("404")
def page_404():
    return "404，当前时间是：%s" % time.ctime()


@route(r"/index\.html")
def index(cookie, call_func):
    if cookie:
        cookie = cookie.split("'")
        cookie = cookie[1]
        # 1. 获取对应的html模板
        db = pymysql.connect(host=DATABASE, port=3306, user='root', password='201314', database='shop',
                             charset='utf8')
        cursor = db.cursor()
        sql = """select user_info.name from user_info inner join cookie on user_info.uid=cookie.uid where cookie.cookie=%s;"""
        cursor.execute(sql, [cookie])  # 为了避免SQL注入，此时用MySQL自带的功能参数化
        name = cursor.fetchone()
        cursor.close()
        db.close()

        with mini_open("/index.html") as f:
            content = f.read()

            content = re.sub(r"\{% name %\}", name[0], content)

        return content
    else:
        redirect(call_func)
        return "302"


@route(r"/login\.html")
def login(*args):
    # 1. 获取对应的html模板
    with mini_open("/login.html") as f:
        content = f.read()

    return content


@route(r"/member\.html")
def member(cookie, call_func):
    # 1. 获取对应的html模板
    if cookie:
        cookie = cookie.split("'")
        cookie = cookie[1]
        # 1. 获取对应的html模板
        db = pymysql.connect(host=DATABASE, port=3306, user='root', password='201314', database='shop',
                             charset='utf8')
        cursor = db.cursor()
        sql = """select user_info.name,user_info.vip from user_info inner join cookie on user_info.uid=cookie.uid where cookie.cookie=%s;"""
        cursor.execute(sql, [cookie])  # 为了避免SQL注入，此时用MySQL自带的功能参数化
        name = cursor.fetchone()
        cursor.close()
        db.close()

        with mini_open("/member.html") as f:
            content = f.read()

            content = re.sub(r"\{% name %\}", name[0], content)
            content = re.sub(r"\{% vip %\}", name[1], content)

        return content
    else:
        redirect(call_func)
        return "302"


@route(r"/shopcar\.html")
def shopcar():
    # 1. 获取对应的html模板
    with mini_open("/shopcar.html") as f:
        content = f.read()

    return content


@route(r"/reg\.html")
def reg(*args):
    """
    username 用户名
    password 密码
    confirm 确认密码

    :return:
    """
    # 1. 获取对应的html模板
    with mini_open("/reg.html") as f:
        content = f.read()

    return content

@route(r"/reg_now\.html")
def reg_now(pots, cookie, call_func):
    # 301重定向
    # 获取用户名和密码 然后转码
    username = pots["username"]
    username = unquote(username)
    password = pots["password"]
    password = unquote(password)
    # 连接数据库
    db = pymysql.connect(host='localhost', port=3306, user='root', password='201314', database='shop',
                         charset='utf8')
    # 获取指针
    cursor = db.cursor()

    # 检测是用户名是否存在
    sql = """select * from user where user_name=%s;"""
    cursor.execute(sql, username)
    if cursor.fetchone():
        cursor.close()
        db.close()
        # 存在直接返回 不写入到数据库
        return "0"
    # 连接数据库
    db = pymysql.connect(host=DATABASE, port=3306, user='root', password='201314', database='shop',
                         charset='utf8')
    cursor = db.cursor()
    # 添加到数据库
    sql = "insert into user values(0,%s,%s);"
    # 执行sql语句
    cursor.execute(sql, [username, password])
    db.commit()
    sql = """select id from user where user_name=%s;"""
    cursor.execute(sql, username)
    id = cursor.fetchone()
    sql = "insert into user_info values(0,'新用户',null,'男',%s,null,null,null,null);"
    # 执行sql语句
    cursor.execute(sql, [id])
    cursor.close()
    db.close()
    # 已经写入到数据库 返回给浏览器结果
    return "1"


@route(r"/checks\.html")
def checks(pots, cookie, call_func):
    """
    登录点击之后事件处理
    :param pots:
    :return:
    """
    print(pots)
    # 获取用户名和密码 然后转码
    username = pots["username"]
    username = unquote(username)
    password = pots["password"]
    password = unquote(password)

    # 连接数据库
    db = pymysql.connect(host='localhost', port=3306, user='root', password='201314', database='shop',
                         charset='utf8')

    cursor = db.cursor()

    # 检测是用户名是否存在
    sql = """select id from user where user_name=%s and password=%s;"""
    cursor.execute(sql, [username, password])
    login_info = cursor.fetchone()
    if login_info:
        cursor.close()
        db.close()
        cookie = "id='%s'" % login_info[0]
        call_func("302 Temporarily Moved",
                  [("Content-Type", "text/html;charset=utf-8"), ("framework", "mini_web"), ("Location", "./index.html"),
                   ("Set-cookie", cookie)])
        set_cookie(cookie, login_info[0])
        return "302"
    ret = "用户名或密码错误"

    return ret


def set_cookie(cookie, id):
    print(cookie)
    cookie = cookie.split("'")
    cookie = cookie[1]
    db = pymysql.connect(host='localhost', port=3306, user='root', password='201314', database='shop',
                         charset='utf8')
    cursor = db.cursor()
    sql = """select * from cookie where cookie=%s;"""
    cursor.execute(sql, cookie)
    cookie_temp = cursor.fetchone()
    print(cookie_temp)
    if cookie_temp:
        print("数据存在")
        cursor.close()
        db.close()
        # 存在直接返回 不写入到数据库
        return

    db = pymysql.connect(host=DATABASE, port=3306, user='root', password='201314', database='shop',
                         charset='utf8')
    cursor = db.cursor()
    # 添加到数据库
    sql = "insert into cookie values(0,%s,%s);"
    # 执行sql语句
    cursor.execute(sql, [cookie, id])
    db.commit()
    # 关闭数据库
    cursor.close()
    db.close()


@route(r"/pwd\.html")
def pwd(cookie, call_func):
    """
    old_password 原密码
    new_password 密码
    confirm 确认密码

    :return:
    """
    # 1. 获取对应的html模板
    if cookie:
        cookie = cookie.split("'")
        cookie = cookie[1]
        # 1. 获取对应的html模板
        db = pymysql.connect(host=DATABASE, port=3306, user='root', password='201314', database='shop',
                             charset='utf8')
        cursor = db.cursor()
        sql = """select user_info.name,user_info.vip from user_info inner join cookie on user_info.uid=cookie.uid where cookie.cookie=%s;"""
        cursor.execute(sql, [cookie])  # 为了避免SQL注入，此时用MySQL自带的功能参数化
        name = cursor.fetchone()
        cursor.close()
        db.close()

        with mini_open("/pwd.html") as f:
            content = f.read()

            content = re.sub(r"\{% name %\}", name[0], content)
            content = re.sub(r"\{% vip %\}", name[1], content)

        return content
    else:
        redirect(call_func)
        return "302"


@route(r"/pwd_ok\.html")
def pwd_ok(pots, cookie, call_func):
    # 判断是否有cookie
    if cookie:
        # 如果有 获取到值
        cookie = cookie.split("'")
        cookie = cookie[1]
        # 1. 获取对应的html模板
        # 链接数据库，获取游标
        db = pymysql.connect(host=DATABASE, port=3306, user='root', password='201314', database='shop',
                             charset='utf8')
        cursor = db.cursor()
        # 打印数据库用户列表信息
        sql_user = "select * from user;"
        cursor.execute(sql_user)
        sql_user_table = cursor.fetchall()
        print("==============")
        print(sql_user_table)
        print("==============")
        # 获取指定id=1的用户 密码
        sql = "select password from user where id=%s;"
        print(cookie)
        cursor.execute(sql, [cookie])
        sql_password = cursor.fetchall()
        print("------>数据库密码", sql_password)
        old_password = pots['old_password']
        print("------>用户输入原始密码", old_password)
        # 将数据库用户密码与网页修改密码进行判断
        if sql_password[0][0] != old_password:
            return "原密码错误，当前时间是: %s" % time.ctime()
        else:
            print("原始密码确认成功")
            # 修改指定id=1的用户 密码
            new_password = pots['new_password']
            sql = "update user set password=%s where id=%s;"
            cursor.execute(sql, [new_password, cookie])
            print("用户数据库密码修改成功")

        return "./login.html"
    else:
        redirect(call_func)
        return "302"

    """
    old_password 原密码
    new_password 密码
    confirm 确认密码

    :return:
    """


def application(env, call_func):
    """
    接收web服务器传递过来的 请求参数
    :param file_path:
    :return:
    """
    # 2. 根据映射的关系即URL_ROUTE这字典，根据不同的url请求调用对应的函数
    # 2.0 提取url中的路径
    file_path = env["PATH_INFO"]  # "/login.html"

    # 2.1 提取函数引用
    for url, func in URL_ROUTE.items():
        # url--->r"/update/\d+.html"
        # func-->show_update_page
        ret = re.match(url, file_path)  # 相当于re.match(r"/update/(\d+)\.html", "/update/300268.html")
        if ret:
            # 如果匹配成功
            # 回调 call_func变量指向的函数，并且将 状态码以及header传递过去
            call_func("200 OK", [("Content-Type", "text/html;charset=utf-8"), ("framework", "mini_web")])

            if env["MODE"] == "HTTP":

                cookie = env.get("COOKIE", None)
                # 调用函数 正则表达式方式加参数
                response_body = func(cookie, call_func)  # response_body = login("/login.html")

                break

            elif env["MODE"] == "POST":
                pots = env["POST"]
                # 这是POTS请求 传入POST传入的信息
                cookie = env.get("COOKIE", None)
                response_body = func(pots, cookie, call_func)
                break

    else:
        # 没有匹配成功
        # 回调 call_func变量指向的函数，并且将 状态码以及header传递过去
        call_func("404 Not Found", [("Content-Type", "text/html;charset=utf-8"), ("framework", "mini_web")])
        # 如果浏览器请求的url没有在 路由映射字典中找到，那么就返回一个默认的404处理函数
        func = URL_ROUTE.get("404", lambda: "not found you page ,404")
        response_body = func()

        # 返回数据给web服务器
    return response_body

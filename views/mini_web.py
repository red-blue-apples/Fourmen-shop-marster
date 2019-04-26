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


@route("404")
def page_404():
    return "404，当前时间是：%s" % time.ctime()


@route(r"/index\.html")
def index():

    # 1. 获取对应的html模板
    with mini_open("/index.html") as f:
        content = f.read()

    # 2. 查询数据
    db = pymysql.connect(host='localhost', port=3306, user='root', password='python', database='stock_db', charset='utf8')
    cursor = db.cursor()
    sql = """select * from info;"""
    cursor.execute(sql)
    data_from_mysql = cursor.fetchall()
    cursor.close()
    db.close()

    # print("\n\n")
    # print(data_from_mysql)

    html_template = """
                    <tr>
                        <td>{0[0]}</td>
                        <td>{0[1]}</td>
                        <td>{0[2]}</td>
                        <td>{0[3]}</td>
                        <td>{0[4]}</td>
                        <td>{0[5]}</td>
                        <td>{0[6]}</td>
                        <td>{0[7]}</td>
                        <td>
                            <input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="{0[1]}">
                        </td>
                    </tr>
                    """

    # 定义一个变量，用来存储查询出来的数据最终要组成的样子的html
    html = ""
    # 循环的次数是根据从MySQL查询出来的记录的个数决定，例如从MySQL中查出来10个记录，那么样子就像((), (), () .... ())
    for one_stock in data_from_mysql:
        html += html_template.format(one_stock)

    # 3. 将查询的数据替换到html模板中
    content = re.sub(r"\{% content %\}", html, content)

    return content


@route(r"/center\.html")
def center():
    # 1. 读取对应HTML模板的数据
    with mini_open("/center.html") as f:
        content = f.read()

    # 2. 从MySQL中查询数据
    db = pymysql.connect(host='localhost', port=3306, user='root', password='python', database='stock_db', charset='utf8')
    cursor = db.cursor()
    sql = """select i.code,i.short,i.chg,i.turnover,i.price,i.highs,j.note_info from info as i inner join focus as j on i.id=j.info_id;"""
    cursor.execute(sql)
    data_from_mysql = cursor.fetchall()
    cursor.close()
    db.close()

    # 3. 找到每行的模板
    html_template = """
                    <tr>
                        <td>{0[0]}</td>
                        <td>{0[1]}</td>
                        <td>{0[2]}</td>
                        <td>{0[3]}</td>
                        <td>{0[4]}</td>
                        <td>{0[5]}</td>
                        <td>{0[6]}</td>
                        <td>
                            <a type="button" class="btn btn-default btn-xs" href="/update/{0[0]}.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
                        </td>
                        <td>
                            <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="{0[0]}">
                        </td>
                    </tr>
                    """

    # 3. 替换
    html = ""
    for one_stock_info in data_from_mysql:
        html += html_template.format(one_stock_info)

    # 通过正则表达式替换 html模板中 变量
    content = re.sub(r"\{% content %\}", html, content)

    return content


@route(r"/update/(\d+)\.html")
def show_update_page(stock_code):
    # 1. 读取HTML模板数据
    with mini_open("/update.html") as f:
        content = f.read()

    # 2. 查询数据库
    # 链接数据库，并查询需要的数据
    db = pymysql.connect(host='localhost', port=3306, user='root', password='python', database='stock_db', charset='utf8')
    cursor = db.cursor()
    sql = """select focus.note_info from focus inner join info on focus.info_id=info.id where info.code=%s;"""
    cursor.execute(sql, [stock_code])  # 为了避免SQL注入，此时用MySQL自带的功能参数化
    stock_note_info = cursor.fetchone()
    cursor.close()
    db.close()

    print("------->>>>>>", stock_note_info)

    # 3. 替换html中的模板变量
    content = re.sub(r"\{% code %\}", stock_code, content)
    content = re.sub(r"\{% note_info %\}", stock_note_info[0], content)

    return content


@route(r"/update/(\d*)/(.*)\.html")
def commit_update_page(stock_code, stock_comment):
    """进行数据的真正更新"""

    # 先对url数据激进型解码
    stock_comment = unquote(stock_comment)

    # 数据库进行修改
    db = pymysql.connect(host='localhost', port=3306, user='root', password='python', database='stock_db', charset='utf8')
    cursor = db.cursor()
    sql = """update focus inner join info on focus.info_id=info.id set focus.note_info=%s where info.code=%s;"""
    cursor.execute(sql, [stock_comment, stock_code])
    db.commit()
    cursor.close()
    db.close()

    return "修改成功"


@route(r"/add/(\d+)\.html")
def add_focus(stock_code):
    """
    添加关注
    :param stock_code:
    :return:
    """

    # 链接数据库，将要关注的股票信息添加到focus数据表
    db = pymysql.connect(host='localhost', port=3306, user='root', password='python', database='stock_db', charset='utf8')
    cursor = db.cursor()
    # 判断是否已经关注
    sql = """select * from focus inner join info on focus.info_id=info.id where info.code=%s;"""
    cursor.execute(sql, [stock_code])
    if cursor.fetchone():
        cursor.close()
        db.close()
        return "已经关注过了，请不要重复关注"

    # 如果没有关注，那么就进行关注
    sql = """insert into focus (info_id) select id from info where code=%s;"""
    cursor.execute(sql, [stock_code])
    db.commit()
    cursor.close()
    db.close()
    return "关注成功"


@route(r"/del/(\d+)\.html")
def del_focus(stock_code):
    """
    取消关注
    :return:
    """
    db = pymysql.connect(host='localhost', port=3306, user='root', password='python', database='stock_db', charset='utf8')
    cursor = db.cursor()

    # 判断是否已经关注
    sql = """select * from focus inner join info on focus.info_id=info.id where info.code=%s;"""
    cursor.execute(sql, [stock_code])
    if not cursor.fetchone():
        cursor.close()
        db.close()
        return "并没有关注，为什么要取消关注呢？不理解，啦啦啦。。。"

    # 如果有关注，那么就进行取消关注
    sql = """delete from focus where info_id = (select id from info where code=%s);"""
    cursor.execute(sql, [stock_code])
    db.commit()
    cursor.close()
    db.close()

    return "取消关注成功"


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

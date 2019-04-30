import random
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
DATABASE = '127.0.0.1'

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
def shopcar(cookie, call_func):
    """
    购物车
    :return:
    """
    cookie = cookie.split("'")
    cookie = cookie[1]
    print(cookie)
    db = pymysql.connect(host=DATABASE, port=3306, user='root', password='201314', database='shop',
                         charset='utf8')
    cursor = db.cursor()
    sql = """select user_info.name from user_info inner join cookie on user_info.uid=cookie.uid where cookie.cookie=%s;"""
    cursor.execute(sql, [cookie])  # 为了避免SQL注入，此时用MySQL自带的功能参数化
    name = cursor.fetchone()

    """========================================="""

    shopcar_temp = """
            <tr class="tr_c">
                <td><input type="checkbox" checked="checked" name="sub"></td>
                <td colspan="2">
                    <table width="100%" border="0" cellspacing="0" cellpadding="0">
                      <tbody><tr>
                        <td width="15%"><img src="{0[3]}"></td>
                        <td width="85%"><a href="#" class="title">{0[1]}</a></td>
                      </tr>
                    </tbody></table>
                </td>
                <td class="price mid-dj">￥{0[2]}</td>
              </tr>
    """
    shopcar = ""
    sql = """select * from commoditys as c left join shopcar as s on s.cid=c.id left join `user` as u on s.uid=u.id WHERE u.id=%s;"""
    cursor.execute(sql, [cookie])  # 为了避免SQL注入，此时用MySQL自带的功能参数化
    car_info = cursor.fetchall()
    print(car_info)
    hj = 0
    for info in car_info:
        print(info)
        shopcar += str(shopcar_temp.format(info))
        hj += info[2]


    with mini_open("/shopcar.html") as f:
        content = f.read()
        content = re.sub(r"\{% name %\}", name[0], content)
        content = re.sub(r"\{% shopcar %\}", str(shopcar), content)
        content = re.sub(r"\{% hj %\}", str(hj), content)

    return content
@route(r"/info\.html")
def info(cookie, call_func):
    cookie = cookie.split("'")
    cookie = cookie[1]
    print(cookie)
    db = pymysql.connect(host=DATABASE, port=3306, user='root', password='201314', database='shop',
                         charset='utf8')
    cursor = db.cursor()
    sql = """select user_info.name from user_info inner join cookie on user_info.uid=cookie.uid where cookie.cookie=%s;"""
    cursor.execute(sql, [cookie])  # 为了避免SQL注入，此时用MySQL自带的功能参数化
    name = cursor.fetchone()
    with mini_open("/info.html") as f:
        content = f.read()
        content = re.sub(r"\{% name %\}", name[0], content)

    return content


@route(r"/info_ok\.html")
def info_ok(post, cookie, call_func):
    # 将字典中的汉字转译
    post['local_information'] = unquote(post['local_information'])
    post['detailed_address'] = unquote(post['detailed_address'])
    post['consignee'] = unquote(post['consignee'])
    # 获取提交订单网页信息
    print("=====获取信息如下====")
    print(post)
    print("===================")
    # 链接数据库
    db = pymysql.connect(host=DATABASE, port=3306, user='root', password='201314', database='shop',
                         charset='utf8')
    print("-------》链接数据库成功")
    # 获取游标
    cursor = db.cursor()
    # 开始上传收货地址订单信息
    try:
        sql = "update adderss set adderss=%s,postal_code=%s,detailed_address=%s,name=%s,phone_num=%s,Tel=%s where id=1;"
        a = post['local_information']
        b = post['postal_code']
        c = post['detailed_address']
        d = post['consignee']
        e = post['mobile_phone']
        f = post['phone']
        cursor.execute(sql, [a, b, c, d, e, f])

        call_func("302 Temporarily Moved",
                  [("Content-Type", "text/html;charset=utf-8"), ("framework", "mini_web"), ("Location", "./payply.html")])


        print("数据库上传信息成功")
        return ""
    except:
        print("数据库上传信息失败")



@route(r"/payply\.html")
def payply(cookie, call_func):
    cookie = cookie.split("'")
    cookie = cookie[1]
    db = pymysql.connect(host=DATABASE, port=3306, user='root', password='201314', database='shop',
                         charset='utf8')
    cursor = db.cursor()
    sql = """select user_info.name from user_info inner join cookie on user_info.uid=cookie.uid where cookie.cookie=%s;"""
    cursor.execute(sql, [cookie])  # 为了避免SQL注入，此时用MySQL自带的功能参数化
    name = cursor.fetchone()

    db = pymysql.connect(host=DATABASE, port=3306, user='root', password='201314', database='shop',
                         charset='utf8')
    cursor = db.cursor()
    sql = """select * from commoditys as c left join shopcar as s on s.cid=c.id left join `user` as u on s.uid=u.id WHERE u.id=%s;"""
    cursor.execute(sql, [cookie])  # 为了避免SQL注入，此时用MySQL自带的功能参数化
    car_info = cursor.fetchall()
    hj = 0
    for info in car_info:
        print(info)
        hj += info[2]



    with mini_open("/payply.html") as f:
        content = f.read()
        content = re.sub(r"\{% name %\}", name[0], content)
        content = re.sub(r"\{% jb %\}", str(hj), content)
    return content

@route("404")
def page_404():
    num = random.randint(1,2)
    page = "/404%d.html"%num
    with mini_open(page) as f:
        content = f.read()
    return content

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

        """==============================pic1======================================"""
        # 这里是 第一个pic的模板
        sql = """select id,name,price,picimg,content from commoditys limit 4;"""
        cursor.execute(sql)  # 为了避免SQL注入，此时用MySQL自带的功能参数化
        pic_info = cursor.fetchall()
        pic1_temp = """
          <form action="./product_show.html" method="post" style="display:inline">
            <li class="pic">
                <p class="p01">{0[1]}</p>
                    <p class="p02">
                        <font>￥</font><b>{0[2]}</b><br/>
                            <span>{0[1]}</span>
                            <input type="hidden" name="id" value="{0[0]}">
                            <input type="submit" value="立即购买" class="buy"/>
                    </p>
                            <img src="{0[3]}" />
                    </li>
                </form>
                """
        # 储存整体模板
        pic1 = ""
        # 获取商品信息
        for info in pic_info:
            pic1 += pic1_temp.format(info)

        """==============================pic2======================================"""

        pic2_temp_one = """
        
                    <div class="item big">
                    <form action="./product_show.html" method="post">
                    <input type="hidden" name="id" value="{0[0]}">
                        <a href="#" class="title">{0[1]}</a>
                        <p>
                            <font>￥{0[2]}</font>
                        </p>
                        <input type="submit" value="" class="buy"/>
                        <img src="{0[3]}" />
                    </form>
                    </div>
        """
        pic2_temp = """
                    <div class="item">
                        <form action="./product_show.html" method="post">
                    <input type="hidden" name="id" value="{0[0]}">
                        <a href="#" class="title">{0[1]}</a>
                        <p>
                            <font>￥{0[2]}</font>
                        </p>
                        <input type="submit" value="" class="buy"/>
                        <img src="{0[3]}" style="width: 180px;" />
                    </form>
                    
                    </div>
        """

        sql = """select id,name,price,picimg,content from commoditys where type=1;"""
        cursor.execute(sql)  # 为了避免SQL注入，此时用MySQL自带的功能参数化
        pic_info = cursor.fetchall()
        pic2 = ""
        pic2 += pic2_temp_one.format(pic_info[0])

        for info in pic_info:
            pic2 += pic2_temp.format(info)

        """==============================pic3======================================"""

        pic3_temp_one = """

                            <div class="item item big" width="281px">
                            <form action="./product_show.html" method="post">
                            <input type="hidden" name="id" value="{0[0]}">
                                <a href="#" class="title">{0[1]}</a>
                                <p>
                                    <font>￥{0[2]}</font>
                                </p>
                                <input type="submit" value="" class="buy"/>
                                <img src="{0[3]}"/>
                            </form>
                            </div>
                """
        pic3_temp = """
                            <div class="item"  width="281px">
                                <form action="./product_show.html" method="post">
                            <input type="hidden" name="id" value="{0[0]}">
                                <a href="#" class="title">{0[1]}</a>
                                <p>
                                    <font>￥{0[2]}</font>
                                </p>
                                <input type="submit" value="" class="buy"/>
                                <img src="{0[3]}" style="width: 180px;" />
                            </form>

                            </div>
                """

        sql = """select id,name,price,picimg,content from commoditys where type=3;"""
        cursor.execute(sql)  # 为了避免SQL注入，此时用MySQL自带的功能参数化
        pic_info = cursor.fetchall()
        pic3 = ""
        pic3 += pic3_temp_one.format(pic_info[0])

        for info in pic_info:
            pic3 += pic3_temp.format(info)

        """==============================pic4======================================"""

        pic4_temp_one = """

                            <div class="item item big" width="281px">
                            <form action="./product_show.html" method="post">
                            <input type="hidden" name="id" value="{0[0]}">
                                <a href="#" class="title">{0[1]}</a>
                                <p>
                                    <font>￥{0[2]}</font>
                                </p>
                                <input type="submit" value="" class="buy"/>
                                <img src="{0[3]}"/>
                            </form>
                            </div>
                """
        pic4_temp = """
                            <div class="item"  width="281px">
                                <form action="./product_show.html" method="post">
                            <input type="hidden" name="id" value="{0[0]}">
                                <a href="#" class="title">{0[1]}</a>
                                <p>
                                    <font>￥{0[2]}</font>
                                </p>
                                <input type="submit" value="" class="buy"/>
                                <img src="{0[3]}" style="width: 180px;" />
                            </form>

                            </div>
                """

        sql = """select id,name,price,picimg,content from commoditys where type=4;"""
        cursor.execute(sql)  # 为了避免SQL注入，此时用MySQL自带的功能参数化
        pic_info = cursor.fetchall()
        pic4 = ""
        pic4 += pic4_temp_one.format(pic_info[0])

        for info in pic_info:
            pic4 += pic4_temp.format(info)
        with mini_open("/index.html") as f:
            content = f.read()

            content = re.sub(r"\{% name %\}", name[0], content)
            content = re.sub(r"\{% pic1 %\}", pic1, content)
            content = re.sub(r"\{% pic2 %\}", pic2, content)
            content = re.sub(r"\{% pic3 %\}", pic3, content)
            content = re.sub(r"\{% pic4 %\}", pic4, content)
        cursor.close()
        db.close()
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


@route(r"/product\.html")
def product(pots, cookie, call_func):
    pots = pots["keyword"]

    """
    :return:
    """
    if cookie:
        cookie = cookie.split("'")
        cookie = cookie[1]
        pro_temp = """
        <div class="item">
        <form action="./product_show.html" method="post">
        <input type="hidden" name="id" value="{0[0]}">
                <dl>
                    <dt><img src="{0[3]}" /></dt>
                    <dd>
                        <img class="on" src="images/img/img39.jpg" /><img src="{0[3]}" /><img
                            src="{0[3]}" />
                    </dd>
                </dl>
                <p class="p01">
                    <font>￥</font>{0[2]}</font>
                </p>
                <p class="p02"><input type="submit" value="{0[1]}"/></p>
                <p class="p03"><span class="sp01">月销量：<b>0</b></span><span>评价：<strong>0</strong></span></p>
            </form>
            </div>
        """
        db = pymysql.connect(host=DATABASE, port=3306, user='root', password='201314', database='shop',
                             charset='utf8')
        cursor = db.cursor()
        sql = """select user_info.name from user_info inner join cookie on user_info.uid=cookie.uid where cookie.cookie=%s;"""
        cursor.execute(sql, [cookie])  # 为了避免SQL注入，此时用MySQL自带的功能参数化
        name = cursor.fetchone()
        pots = "%" + pots + "%"
        sql = """select id,name,price,picimg,content from commoditys where name like %s;"""
        cursor.execute(sql, pots)  # 为了避免SQL注入，此时用MySQL自带的功能参数化
        pro_info = cursor.fetchall()
        pro = ""
        for info in pro_info:
            pro += pro_temp.format(info)

        with mini_open("/product.html") as f:
            content = f.read()
            print("=========", name)
            content = re.sub(r"\{% name %\}", name[0], content)
            content = re.sub(r"\{% pro_cont %\}", pro, content)

        cursor.close()
        db.close()
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


@route(r"/member_now\.html")
def member_now(post, oookie, call_func):
    cookie = oookie.split("'")
    cookie = cookie[1]
    print("==============")
    print(post)
    # 获取用户信息
    print("==============")
    # 提取用户出来的资料
    new_password = unquote(post['user_name'])
    print(new_password)
    user_id = unquote(post['user_id'])  # 身份证id
    # yinghan_name = unquote(post['user_yinghan'])  # 对应uid
    yinghan_num = unquote(post['yinghan_num'])  # 对应bank
    email = unquote(post['emali'])  # 邮箱
    print(email)
    address = unquote(post['address'])  # 地址
    db = pymysql.connect(host=DATABASE, port=3306, user='root', password='201314', database='shop',
                         charset='utf8')

    cursor = db.cursor()
    # 检测是用户名是否存在
    sql = """select * from user_info where name=%s"""
    cursor.execute(sql, new_password)
    if cursor.fetchone():
        cursor.close()
        db.close()
        # 存在直接返回 不写入到数据库
        return "0"
    # sql_user = "select * from user_info;"  # 查询一下
    # sql_user_table = cursor.execute(sql_user)
    # print("==============")
    # print(sql_user_table)
    # print("==============")

    # sqls = """update user_info inner join info on focus.info_id=info.id set focus.note_info=%s where info.code=%s;"""
    db = pymysql.connect(host=DATABASE, port=3306, user='root', password='201314', database='shop',
                         charset='utf8')
    # 修改
    sql = "update user_info set name=%s,pid=%s,email=%s,adds=%s where uid=%s;"
    cursor.execute(sql, [new_password, user_id, email, address, cookie])
    # db.commit()   # 提交
    cursor.close()
    db.close()
    return "用户修改数据成功"





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
    db = pymysql.connect(host=DATABASE, port=3306, user='root', password='201314', database='shop',
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
    sql = "insert into user_info values(0,'新用户',null,'男',%s,null,null,null,'青铜会员');"
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


@route(r"/product_show\.html")
def product_show(post, cookie, call_func):
    """
    :param cookie: cookie记录登录状态和用户信息
    :param call_func: 回调状态函数
    :return:
    """
    print(post)
    if cookie:
        cookie = cookie.split("'")
        cookie = cookie[1]
        post = post["id"]
        # 1. 获取对应的html模板
        db = pymysql.connect(host=DATABASE, port=3306, user='root', password='201314', database='shop',
                             charset='utf8')
        cursor = db.cursor()
        sql = """select user_info.name from user_info inner join cookie on user_info.uid=cookie.uid where cookie.cookie=%s;"""
        cursor.execute(sql, [cookie])  # 为了避免SQL注入，此时用MySQL自带的功能参数化
        name = cursor.fetchone()
        # 这里是 第一个pic的模板
        sql = """select * from commoditys where id=%s;"""
        cursor.execute(sql, post)  # 为了避免SQL注入，此时用MySQL自带的功能参数化
        pic_info = cursor.fetchall()
        print(pic_info)

        with mini_open("/product_show.html") as f:
            content = f.read()
            # 渲染名字
            content = re.sub(r"\{% name %\}", name[0], content)
            # 渲染商品图
            content = re.sub(r"\{% img %\}", pic_info[0][4], content)
            # 渲染简介
            content = re.sub(r"\{% particulars %\}", pic_info[0][5], content)
            # 渲染商品名称
            content = re.sub(r"\{% cname %\}", pic_info[0][1], content)
            # 渲染商品介绍
            content = re.sub(r"\{% content %\}", pic_info[0][6], content)
            # 渲染商品价格
            price = str(pic_info[0][2])
            content = re.sub(r"\{% price %\}", price, content)
            content = re.sub(r"\{% cid %\}", str(pic_info[0][0]), content)

            sql = """select user_info.name from user_info inner join cookie on user_info.uid=cookie.uid where cookie.cookie=%s;"""
            cursor.execute(sql, [cookie])  # 为了避免SQL注入，此时用MySQL自带的功能参数化
            name = cursor.fetchone()
            # 这里是 第一个pic的模板
            sql = """select id,name,price,picimg,content from commoditys limit 4;"""
            cursor.execute(sql)  # 为了避免SQL注入，此时用MySQL自带的功能参数化
            pic_info = cursor.fetchall()

            left_temp = """
            <form action="./product_show.html" method="post" style="display:inline">
            <input type="hidden" name="id" value="{0[0]}">
            <div class="item">
                        	<ul>
                                <li><img src="{0[3]}" id="submit" width="160" height="160"/></li>
                                
                                <li class="title"><input type="submit" value="{0[1]}" style="cursor:pointer;" /></li>
                                <li class="price">￥{0[2]}</li>
                            </ul>
                        </div>
                        
            </form>
            """
            left = ""
            # 获取商品信息

            for info in pic_info:
                left += left_temp.format(info)
            content = re.sub(r"\{% left %\}", left, content)

        cursor.close()
        db.close()
        return content
    else:
        redirect(call_func)
        return "302"
@route(r"/addcar\.html")
def addcar(post, cookie, call_func):
    cookie = cookie.split("'")
    cookie = cookie[1]
    cid = post["cid"]
    uid = cookie
    db = pymysql.connect(host=DATABASE, port=3306, user='root', password='201314', database='shop',
                         charset='utf8')
    cursor = db.cursor()
    # 添加到数据库
    sql = "insert into shopcar values(0,%s,%s);"
    # 执行sql语句
    cursor.execute(sql, [uid,cid])
    db.commit()
    cursor.close()
    db.close()
    return "ok"


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
                post = env["POST"]
                # 这是POTS请求 传入POST传入的信息
                cookie = env.get("COOKIE", None)
                response_body = func(post, cookie, call_func)
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

import requests
import time
import json
from pymongo import MongoClient
import pymongo
import urllib3
import random
import re
urllib3.disable_warnings()
from bs4 import BeautifulSoup


"""
爬取微信公众号文章的正文、阅读数、点赞数、发布时间、url、正文、封面图片、评论
写入json文件、数据库中
参考文献：https://blog.csdn.net/qq_41686130/article/details/88296981
"""
sleepTime = 2
def getWechatMessageUrlList(begin=0):
    """
    从微信公众号订阅平台获得某个公众号的所有历史文章url
    :param begin: 开始页数，一页5篇文章，第二页5开始
    :return: 所有历史文章链接集合
    """
    #
    url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
    token = "544176708"
    Cookie = "appmsglis                                              t_action_3867517163=card; RK=ir4BjYWzE9; ptcz=6d1d39d5593df9fe0aa1c98a6ef93b0c778bf2d68fd7df31772ec5f1ee23f503; pgv_pvi=3058238464; pgv_pvid=903954968; luin=o1162008006; lskey=00010000d5da4e4ae65c0540c18b79c4d8a3725b1040ec487a302f01d0e3a446743d0800ebda3faecce7730e; o_cookie=1162008006; pac_uid=1_1162008006; ua_id=ABh4oVZmSYUDufjvAAAAAHqdfN2AQ0p78pGvcDN-1hs=; noticeLoginFlag=1; mm_lang=zh_CN; bizuin=3867517163; remember_acct=linjie%40seu.edu.cn; pgv_si=s4726671360; uuid=c513648c6a7eefdd937becf61de4459a; ticket=1344f4c6b8f63e318e4798e2ef2545f9fbb37382; ticket_id=gh_e590ec3e0d05; cert=0abwECjz3iribO4e2mqR9mIPjAbms0km; rand_info=CAESIHXXVFuKV7bw7E7uS56KWzSY5f44MRxUXZ5qqjTq7tr5; slave_bizuin=3867517163; data_bizuin=3867517163; data_ticket=DAvqjxvNOyeRxGtclaccf0XTmOYOqHUVARwlL2qAmjgW8zAt74142QK1CYsRhzt5; slave_sid=Z2I1RmRJVjNqNEtCTmVwcVdoajRta2lUdjlxMzRodmc1NGJPQXN3VlNmZUZZRUFFOTVsWVhnM3lBTTRpZ1doN1FyZU43ZXpGVk1BaW83ZXRmUE9Td3lJOE9kWHJBSHZ6TmhhcktaYUFPbkJqaDdBRHg3eWRHRnFaUTFDSk5qY0xlYzVNNWFlaXowQWRFU2Zq; slave_user=gh_e590ec3e0d05; xid=; openid2ticket_o66CF5vnGm9rkGw_M5lzMJ7l1vbk=r8iTNpPHUVVj0DQ2pS8jZ4c0CEK+Ph5i+LgbRgJ0gwI=; rewardsn=; wxtokenkey=777"
    headers = {
        "Cookie": Cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
    }
    # fakeid是公众号独一无二的一个id，等同于后面的__biz
    # 局座召忠 fakeid = "MzIxNDEzNzI4Mg=="
    # 烽火戏诸侯MzA5OTEwMTExMg==

    fakeid = 'MjM5NjQxMDE2MQ=='
    type = '9'  # type在网页中会是10，但是无法取到对应的消息link地址，改为9就可以了

    data1 = {
        "token": token,
        "lang": "zh_CN",
        "f": "json",
        "ajax": "1",
        "random": random.random(),
        "action": "list_ex",
        "begin": begin,  # begin字段表示页数 第一页0，第二页5.。。。
        "count": "5",
        "query": "",
        "fakeid": fakeid,
        "type": type,
    }
    UrlList_json = requests.get(url, headers=headers, params=data1, verify=False).json()

    messageSeveralInfo = []
    if "app_msg_list" in UrlList_json:
        for item in UrlList_json["app_msg_list"]:
            # 提取每页文章的标题及对应的url
            url = item['link']
            info = {   #字典
                "url": item['link'],  # 每篇公众号的链接
                "title": item['title'],
                "digest": item['digest'],
                "create_time": getDate(item['create_time']),
                "update_time": getDate(item['update_time']),
                "cover_image": item['cover'],
                "aid": item['aid'],
                "appmsgid": item['appmsgid'],
            }
            #print("\ntitle: " + info["title"] + ' ' + info["update_time"] )
            messageSeveralInfo.append(info)
    print(messageSeveralInfo)
    time.sleep(sleepTime)
    return messageSeveralInfo
def rmHtmlTags(html):
    """
    去除html标签
    :param html: html页面
    :return: 文章正文（去除标签）
    """
    soup = BeautifulSoup(html, 'html.parser')
    contentWithNoTags = soup.get_text()
    return contentWithNoTags

def getContent(link):
    """
    get the content of a passage link
    :param passage link:
    :return:
    """
    #   从微信公众号订阅平台获得某个公众号的所有历史文章url
    _biz, mid, sn, idx = getInfoForConstructRequests(link)
    url = "https://mp.weixin.qq.com/s"
    token = "544176708"
    Cookie = "appmsglist_action_3867517163=card; RK=ir4BjYWzE9; ptcz=6d1d39d5593df9fe0aa1c98a6ef93b0c778bf2d68fd7df31772ec5f1ee23f503; pgv_pvi=3058238464; pgv_pvid=903954968; luin=o1162008006; lskey=00010000d5da4e4ae65c0540c18b79c4d8a3725b1040ec487a302f01d0e3a446743d0800ebda3faecce7730e; o_cookie=1162008006; pac_uid=1_1162008006; ua_id=ABh4oVZmSYUDufjvAAAAAHqdfN2AQ0p78pGvcDN-1hs=; pgv_si=s7109054464; cert=Ir2ohz9dhviPNXAwYatiVlcr60OwZ8NW; openid=oiID25TZai_v8e8jjxumFhaIaCiY; uuid=42c2af4953b44d8a59508b68783efbff; media_ticket=7afef3b1178da3643692af4eddce9e608cfbee48; media_ticket_id=gh_54344a971abb; noticeLoginFlag=1; pgv_info=ssid=s5570298260; sig=h01ebc14621ccde8a31b20273ad0c4f35622a9e33e2a55a0dd1aeb32b1f1d453fd60039ba4744f8e4e1; data_bizuin=3867517163; data_ticket=oGlDXvRYqhAeqFFDdfibRkKhCpR06mL4GAg1XcMp4fDzbgXLW11OxhLz1mZKBIqR; master_key=UUJwyqZCwlRmZ0dL9BicKQj2J6xDklpe8P0nHI/JEZU=; master_user=gh_e590ec3e0d05; master_sid=ZFJKbmR5cTdLTGtjNGdCYzFCY2xBYVB5X0dCanU3R2FhRDM3XzhwNXp1WG03X0RIRnpUSGN6Q2QxUGFDNUZhbVJTMTRXSVFYZVRTbGVZZ2Y1T2VRWWFlUHQ0dWx4SEhJQWF4NXoyYjA1T09DaXRmaEwya3dhTUNYMXc0YUQ5ekRtcnNNeHdzcUg4WHJmVjhO; master_ticket=33b6e7024d5f3c6ba4f1ca4b48c6deb3; bizuin=3867517163; slave_user=gh_e590ec3e0d05; slave_sid=UEQ4SWt6Vno5RnF2ZXRLV2w1OTd0Vnp1ejhkbmJKRVFNWUlHMzE0MHRwWktaaUFvTmxFSzdUXzk4RXpxWVhxazUzQ3hPUUtQd1I5dGo4M1VGb3lzZ0dSRDdBaldrejN5WUNLWUVqMXc2emdZa3pId04zUkxLV3JjNnRkbWc0QThRZ2c4ZExvVng3bFdoeURj"
    headers = {
        "Cookie": Cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36",
    }

    #   局座召忠
    # fakeid = "MzIxNDEzNzI4Mg=="  # fakeid是公众号独一无二的一个id，等同于后面的__biz
    fakeid = 'MjM5NjQxMDE2MQ=='
    type = '9'  # type在网页中会是10，但是无法取到对应的消息link地址，改为9就可以了

    data1 = {
        "__biz": _biz,
        "mid": mid,
        "f": "json",
        "idx": idx, #idx会变，不能简单设为1就可以了
        "sn": sn,
        "scene": "21",
        "token": "5",
        "lang": "zh_CN",
    }
    content_json = requests.get(url, headers=headers, params=data1, verify=False).json()
    '''
    有用的字段："round_head_img": "title": "desc": "content_noencode": "create_time": "comment_id": 
    '''
    messageContent = {}
    if  "round_head_img" in content_json:
        messageContent["content_roundHeadImg"] = content_json["round_head_img"]
        messageContent["content_title"] = content_json["title"]
        messageContent["content_desc"] = content_json["desc"]
        messageContent["content_createtime"] = content_json["create_time"]
        messageContent["content_commentid"] = content_json["comment_id"]
        messageContent["content_noencode"] = rmHtmlTags(content_json["content_noencode"])
        print(messageContent["content_noencode"])
    #print(messageContent)
    return messageContent

# 毫秒数转日期
def getDate(times):
    timearr = time.localtime(times)
    date = time.strftime("%Y-%m-%d %H:%M:%S", timearr)
    return date


def getInfoForConstructRequests(link):
    """
    get some params of a passage link
    :param link:
    :return params:_biz, mid, sn, idx
    """
    # 获得mid,_biz,idx,sn 这几个在link中的信息
    _biz = link.split("&")[0].split("_biz=")[1]
    mid = link.split("&")[1].split("=")[1]
    sn = link.split("&")[3].split("=")[1]
    idx = link.split("&")[2].split("=")[1]
    return _biz, mid, sn, idx


def getReadLikeNum(link):  #从Fiddler抓取参数
    """
    获取阅读数&点赞数
    :param link: 文章链接
    :return: 阅读数&点赞数
    """
    _biz, mid, sn, idx = getInfoForConstructRequests(link)
    # 目标url
    getappmsgext_url = "http://mp.weixin.qq.com/mp/getappmsgext"

    # fiddler 中取得一些不变的信息
    req_id = "1421f4lDzAJaQhFRq2BMVPhu"  # 需要更新
    pass_ticket = "tpGkOTF/E10ygoyrfPPBezRWXlGZ6Zx0hNlTzg4+7d3bALfPBR1peRStdpRJGa4o"
    appmsg_token = "1083_A6aJZvW9FVKRBOP7Zw-kx7boMiRiDqMAqViWKR2liQVubdhou9OgWzZXXdU8s-9eHRWsRq82hICIkGgZ"
    PCCookie = "rewardsn=; wxuin=1292286712; devicetype=Windows10x64; version=62090538; lang=zh_CN; pass_ticket=tpGkOTF/E10ygoyrfPPBezRWXlGZ6Zx0hNlTzg4+7d3bALfPBR1peRStdpRJGa4o; wap_sid2=CPj1mugEEooBeV9ITGhLd29YclgtamZSMnBKOURWSXY0dTlCQkN3eWl0SmJIcnpRVGRaRl9lekpVclMzZkZtRFYxTWxDQTFKTkR1eW5ES3ZtbnpJN3BVM2Q1NTJ4X21MbXE5RnNqVGRyRHBpWWdZSmluN2tWc1V4WFJidVZZclBsX0dvU3Q4TXRzSnRCZ1NBQUF+MK6rm/wFOA1AAQ==; wxtokenkey=777"
    headers = {
        "Cookie": PCCookie, #phoneCookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 QBCore/3.53.1159.400 QQBrowser/9.0.2524.400 Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat"
    }

    data = {
        "is_only_read": "1",
        "req_id": req_id,
        "pass_ticket": pass_ticket,
        "is_temp_url": "0",
        "appmsg_type" : "9",
    }
    """
    添加请求参数
    __biz对应公众号的信息，唯一
    mid、sn、idx分别对应每篇文章的url的信息，需要从url中进行提取
    key、appmsg_token从fiddler上复制即可
    pass_ticket对应的文章的信息，也可以直接从fiddler复制
    """
    params = {
        "__biz": _biz,
        "mid": mid,
        "sn": sn,
        "idx": idx,
        "key": "777",
        "pass_ticket": pass_ticket,
        "appmsg_token": appmsg_token,
        "uin": "777",
        "wxtoken": "777",
    }
    print(params)
    # 使用post方法进行提交
    content = requests.post(getappmsgext_url, headers=headers, data=data, params=params).json()
    print(content)
    # 提取其中的阅读数和点赞数
    readNum = content["appmsgstat"]["read_num"]
    likeNum = content["appmsgstat"]["like_num"]

    time.sleep(sleepTime)
    return readNum, likeNum, _biz, mid, sn, idx

# test Field
#test_link = "https://mp.weixin.qq.com/s?__biz=MjM5NjQxMDE2MQ==&mid=2650878844&idx=1&sn=014f5708db228164941322be87c86f3e&chksm=bd1c35228a6bbc34f6a7ddb75ed960d686aeeb74473dc994e5d877575c7944c0fb4dd6607869&token=1010720944&lang=zh_CN#rd"
#print(getContent(test_link))
# print(getReadLikeNum(test_link))

def getComments(link):    #从Fiddler抓取参数
    """
    获取评论
    :param link:文章链接
    :return: 评论
    """
    _biz, mid, sn, idx = getInfoForConstructRequests(link)
    getcomment_url = "https://mp.weixin.qq.com/mp/appmsg_comment?action=getcomment&__biz={}&idx={}&comment_id={}&limit=100"

    # fiddler 中取得一些不变的信息
    req_id = "1421f4lDzAJaQhFRq2BMVPhu"  # 需要更新
    pass_ticket = "tpGkOTF/E10ygoyrfPPBezRWXlGZ6Zx0hNlTzg4+7d3bALfPBR1peRStdpRJGa4o"
    appmsg_token = "1083_A6aJZvW9FVKRBOP7Zw-kx7boMiRiDqMAqViWKR2liQVubdhou9OgWzZXXdU8s-9eHRWsRq82hICIkGgZ"
    PCCookie = "rewardsn=; wxuin=1292286712; devicetype=Windows10x64; version=62090538; lang=zh_CN; pass_ticket=tpGkOTF/E10ygoyrfPPBezRWXlGZ6Zx0hNlTzg4+7d3bALfPBR1peRStdpRJGa4o; wap_sid2=CPj1mugEEooBeV9ITGhLd29YclgtamZSMnBKOURWSXY0dTlCQkN3eWl0SmJIcnpRVGRaRl9lekpVclMzZkZtRFYxTWxDQTFKTkR1eW5ES3ZtbnpJN3BVM2Q1NTJ4X21MbXE5RnNqVGRyRHBpWWdZSmluN2tWc1V4WFJidVZZclBsX0dvU3Q4TXRzSnRCZ1NBQUF+MK6rm/wFOA1AAQ==; wxtokenkey=777"
    headers = {
        "Cookie": PCCookie,  # phoneCookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 QBCore/3.53.1159.400 QQBrowser/9.0.2524.400 Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat"
    }


    data = {
        "is_only_read": "1",
        "req_id": req_id,
        "pass_ticket": pass_ticket,
        "is_temp_url": "0",
        "appmsg_type": "9",
    }

    res_commentid = requests.get(link, data=data, verify=False) #comment_id就在文章中
    # 使用正则提取comment_id
    if "comment_id" in res_commentid.text:  #可能该微信文章违规被封
        comment_id = re.findall(r'comment_id = "\d+"',
                            res_commentid.text)[0].split(" ")[-1][1:-1]

    try:
        url = getcomment_url.format(_biz, idx, comment_id)
        comment_json = requests.get(url, headers=headers, verify=False).json()
        comment = {}
        #有用的 "elected_comment": "elected_comment_total_cnt": "only_fans_can_comment":
        comment["elected_comment"] = comment_json["elected_comment"]
        comment["elected_comment_total_cnt"] = comment_json["elected_comment_total_cnt"]
        comment["only_fans_can_comment"] = comment_json["only_fans_can_comment"]

    except Exception as e:
        comment = {}
    return comment




# 写入数据库
def putIntoMogo(InfoList):
    localhost = "127.0.0.1"
    port = 27017

    # 连接数据库
    client = pymongo.MongoClient(host = "localhost", port = port)
    # 建库
    db= client.seu_dndx
    # 建表
    wx_message_sheet = db.seu_dndx_message

    # 存
    for message in InfoList:
        insert_id = wx_message_sheet.insert_one(message)
        print(insert_id)

def save_json(fname, data):
    """
    存json文件
    :param fname: 文件位置
    :param data: 数据
    :return:
    """
    assert isinstance(fname, str)
    if ".json" not in fname:
        raise IOError("fname must be json", fname)
    with open(fname, "a+", encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=4))
            f.write("\n")


# 最大值365，所以range中就应该是73,15表示前3页
#test_link = "https://mp.weixin.qq.com/s?__biz=MjM5NjQxMDE2MQ==&mid=2650873492&idx=1&sn=b386e88d6ab6ed093d38bfd137c8ec61&chksm=bd1c18ca8a6b91dcf7fd89026bd507449176f33846373055650a7b8809c35a1355bbcc760045&token=1010720944&lang=zh_CN#rd"
#print(getComments(test_link))
#getReadLikeNum(test_link)
messageAllInfo = []

if __name__ == '__main__':
    #第一页 0  0-4
    #第二页 5  5-9
    #第三页 10 10-14
    #东南大学 一共423页
    #414继续
    for i in range(418,423):
        print("Page: ",i)
        messageAllInfo = []
        UrlInfoList = getWechatMessageUrlList(i * 5)
        for item in UrlInfoList:
            temp_readNum, temp_LikeNum, _biz, mid, sn, idx = getReadLikeNum(item["url"])
            print("\n题目:" + item['title'] + "\t时间："+ item["update_time"] +"\n"+ item["digest"] +"\n阅读数：" + str(temp_readNum) +"\t点赞数：" +str(temp_LikeNum))
            temple = {
                "title": item['title'],
                "readNum": temp_readNum,
                "likeNum": temp_LikeNum,
                "digest": item['digest'],
                "create_time": item['create_time'],
                "update_time": item['update_time'],
                "url": item['url'],
                "cover_image": item['cover_image'],
                "aid": item['aid'],
                "appmsgid": item['appmsgid'],
                "_biz": _biz,
                "mid": mid,
                "sn": sn,
                "idx": idx,
            }
            #得到评论
            comments_temple = getComments(item['url'])
            content = getContent(item['url'])
            #往dict里加入键值对
            temple = dict(temple, **content)
            temple = dict(temple, **comments_temple)

            messageAllInfo.append(temple)
            #print(temple)
            save_json("seu_dndx.json",temple)
            temple = {}


        putIntoMogo(messageAllInfo)
        print("第"+ str(i + 1) + "页存入数据库成功！")

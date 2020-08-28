#!/usr/bin/env python
#coding: utf-8

#from __future__ import division
import os
import time
import datetime
import threading
import schedule
import configparser
import re
import sys
import hashlib
import random
from wxpy import *
#from xpinyin import Pinyin


from init import analyze
#from init import express
from init.logger import logger
from init import xiaoyu
from init import xiaodou
from init import jianbao
from init import diyi
from importlib import reload
reload(sys)
#sys.setdefaultencoding('utf8')



class GroupMessage():
    #从配置文件获取参数，初始化变量
    def __init__(self):
        self.log_flag = 0
        cf = configparser.ConfigParser()
        if os.path.exists('config/my.conf'):
            cf.read('config/my.conf')
        else:
            cf.read('config/wechat.conf')
        self.path = cf.get('wechat', 'path')
        group_names = cf.get('wechat', 'group_name')
        self.group_list=group_names.strip(',').split(',')
        self.friend_name = cf.get('wechat','friends')
        self.torla_name = cf.get('wechat','group')
        self.welcome_word = cf.get('wechat','welcome_word')
        self.newcomer = cf.get('wechat','newcomer')
        self.recev_mps = int(cf.get('wechat','recev_mps'))
        self.use_xiaoi = int(cf.get('wechat','xiaoi'))
        self.key = cf.get('wechat','key')
        self.secret = cf.get('wechat','secret')
        self.xiaodou_key = cf.get('wechat','xiaodou_key')
        self.friends_accept = cf.get('wechat','friends_accept')
   
        self.invite_group1 = cf.get('wechat','invite_group1')
        self.invite_group2 = cf.get('wechat','invite_group2')
 
        self.send_morning = u'@all 早上好'
        self.send_night = u'@all 晚安哦'
        group_note = cf.get('wechat', 'group_note')
        self.group_note_list=group_note.strip(',').split(',')
        group_jianbao = cf.get('wechat', 'group_jianbao')
        self.group_jianbao_list=group_jianbao.strip(',').split(',')
        group_newcomer = cf.get('wechat', 'group_newcomer')
        group_newcomer1 = cf.get('wechat', 'group_newcomer1')
        self.group_newcomer_list=group_newcomer.strip(',').split(',')
        self.group_newcomer_list1=group_newcomer1.strip(',').split(',')
        self.send_time = cf.get('wechat', 'send_time')
        self.send_talks = cf.get('wechat', 'send_talks')
     
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        self.talk_path = os.path.join(self.path, 'talks')
        if not os.path.exists(self.talk_path):
            os.mkdir(self.talk_path)
        self.members_path = os.path.join(self.path, 'members')
        if not os.path.exists(self.members_path):
            os.mkdir(self.members_path)
        self.friends_path = os.path.join(self.path, 'friends')
        if not os.path.exists(self.friends_path):
            os.mkdir(self.friends_path)
        self.friends_pic_path = os.path.join(self.path, 'friends', 'pic')
        if not os.path.exists(self.friends_pic_path):
            os.mkdir(self.friends_pic_path)

        self.xiaoi = XiaoI(self.key, self.secret)
        self.xiaoyuer = xiaoyu.XiaoY()
        self.xiaodou = xiaodou.Xiaodou(self.xiaodou_key)

        self.send_me = 1

    def init_group_name(self):
        self.group__newcomer = []


    def login(self):
        self.bot = Bot(cache_path=True, console_qr=False)
        #self.bot.enable_puid()
        self.myself = self.bot.self
        try:
            self.friend = self.bot.friends().search(self.friend_name)[0]
        except:
            self.friend = self.bot.self
     
        #print self.bot.friends()
        #logger.info(self.bot.groups())
        #print self.bot.mps()

    def create_group_logfile(self):
        group = self.bot.groups(update=True)
        logger.info(group)
        for gs in group:
            group_name = hashlib.md5(gs.name.encode('utf-8')).hexdigest()[-8:]
            logger.info(gs)
            logger.info(group_name)
            log_file = os.path.join(self.path,group_name)
            if not os.path.exists(log_file):
                os.mkdir(log_file)
        

    def send_friend_msg(self,send_msg):
        logger.info("send message to beijing group")
        self.torla = self.bot.groups().search(u'北京交友群')[0]
        self.torla.send(send_msg)
    def send_kevin_msg(self):
        now_time = time.asctime( time.localtime(time.time()) )
        self.kevin_m = self.bot.friends().search('Kevin')[0]
        self.kevin_m.send(now_time)

    def send_group_msg(self):
        now_time = datetime.datetime.now().strftime("%H:%M")
        if now_time > '09:00' and now_time < '23:00':
            topic_f = open("material/topic.txt","r")
            comment = topic_f.readlines()
            comment_filter = []
            for co in comment:
                if not co.startswith('#'):
                    comment_filter.append(co)
            #print len(comment_filter)
            one_topic = comment_filter[random.randint(0,len(comment_filter)-1)]
    
            self.group_jiaoyou = self.bot.groups().search(u'北京交友群')[0]
            #self.group_jiaoyou1 = self.bot.groups().search(u'测试专用群')[0]
            self.group_jiaoyou.send(one_topic)

        timer = threading.Timer(7200, self.send_group_msg)
        timer.start()

    def msg_from_friends(self):
        @self.bot.register(Friend)
        def msg_yy(msg):

            #create log file
            day = time.strftime("%Y-%m-%d")
            file_name = '%s.txt' % ( day)
            file_ab_path = os.path.join(self.friends_path, file_name)
            create_time = msg.create_time.strftime('%Y-%m-%d %H:%M:%S')
            #pic_file = os.path.join(self.path,group_name,day)
                #if not os.path.exists(pic_file):
                #os.mkdir(pic_file)
    
            #ret_text, self.use_xiaoi = self.xiaoyuer.do_reply(msg,self.use_xiaoi)
            
            #微信web版无法邀请好友入群

            if msg.type == PICTURE:
                word_text = "PICTURE:%s" % ( msg.file_name) 
                ct = msg.create_time.strftime('%Y-%m-%d-%H-%M-%S')
                msg.get_file('%s/%s-%s-%s' % (self.friends_pic_path,ct,random.randint(1,10),msg.file_name))
                #if msg.file_name.endswith(".png"):
                 #   new_friend = self.bot.friends().search(msg.sender.name)[0]
                  #  group_add = self.bot.groups().search(self.invite_group2)[0]
                   # group_add.add_members(new_friend, use_invitation=True)
                    #group_beijing = self.bot.groups().search(self.invite_group3)[0]
                    #group_beijing.add_members(new_friend, use_invitation=True)

            elif msg.type == TEXT:
                word_text = msg.text
                '''
                print self.friends_accept
                #if  self.friends_accept and (u'我通过了你的朋友验证请求' in msg.text or u"现在我们可以开始聊天了" in msg.text):
                if  self.friends_accept and u'我通过了你的朋友验证请求' in msg.text:
                    msg.reply('嗨，您好！欢迎你加入芊芊结北京单身群，为了保证群内良好的交流与互动，请进群后务必根据群要求修改群名片，并完成相应步骤，你才能更好脱单哦！！')
                    new_friend = self.bot.friends().search(msg.sender.name)[0]
                    group_add = self.bot.groups().search(self.invite_group1)[0]
                    group_add.add_members(new_friend, use_invitation=True)
                    msg.reply_raw_msg(
                    raw_type=42,
                    raw_content='<msg username="ddyfy1991" nickname="豆豆要发芽"/>') 
                    msg.reply(u'另外如若想进入其他北京地区单身群，需要做点小任务哦！将以下图片转发到朋友圈，并配上以下文字。完成后将截图发送给我即可。文字内容如下：')
                    msg.reply(u"”这个平台不错哦，群主也很靠谱，大家可以扫描加入，体验一下“")
                    msg.reply_image("material/welcome.jpg")
                elif msg.text == u'入群' or msg.text == "加群":
                    msg.reply('回复相应数字即可发送群邀请\n1. 北京芊芊结1群\n\
2. 北京芊芊    结C群\n3. 缘来是你北京交友群\n4. 机器人小鱼儿聊天群')    
                elif msg.text == u'3':
                    msg.reply('缘来是你北京交友群')    
                    new_friend = self.bot.friends().search(msg.sender.name)[0]
                    group_beijing = self.bot.groups().search(u'北京交友群')[0]
                    group_beijing.add_members(new_friend, use_invitation=True)
                elif msg.text == u'1':
                    msg.reply('北京芊芊结1群')    
                    new_friend = self.bot.friends().search(msg.sender.name)[0]
                    group_add = self.bot.groups().search(u'北京芊芊结1群')[0]
                    group_add.add_members(new_friend, use_invitation=True)
                elif msg.text == u'4':
                    msg.reply('机器人小鱼儿聊天群')    
                    new_friend = self.bot.friends().search(msg.sender.name)[0]
                    group_add = self.bot.groups().search(u'机器人小鱼儿聊天群')[0]
                    group_add.add_members(new_friend, use_invitation=True)
                elif msg.text == u'2':
                    msg.reply('北京芊芊结C群')    
                    new_friend = self.bot.friends().search(msg.sender.name)[0]
                    group_add = self.bot.groups().search(u'北京芊芊结C群')[0]
                    group_add.add_members(new_friend, use_invitation=True)
                elif msg.text == u'5':
                    msg.reply('北京芊芊结单身5群')    
                    new_friend = self.bot.friends().search(msg.sender.name)[0]
                    group_add = self.bot.groups().search(u'北京芊芊结单身5群')[0]
                    group_add.add_members(new_friend, use_invitation=True)
            
            '''
            #if msg.sender.name == 'Kevin':
             #   try:
              #      send_kevin =12
               #     if send_kevin == 1:
                #        msg.reply('Hello')
                #except Exception as e:
                 #   logger.error(e)
                #msg.reply(u'这话我没法接')

            if msg.text == u'你好':
                try:
                    msg.reply(u'你好') 
                except Exception as e:
                    logger.error(e)
            word = "%s %s:%s\n" % (create_time, msg.sender.name, word_text)
            with open(file_ab_path, "a+") as f:
                f.write(word.encode('utf-8'))
                word = None

    #处理公共号消息
    def my_mps(self):
        @self.bot.register(MP)
        def print_mp_msg(msg):
            #self.friend.send(msg)
            #self.friend.send_raw_msg( raw_content=msg.raw)
            #msg.forward(self.friend)
            """
            if msg.type == SHARING and msg.sender.name == '爱净意':
                for article in msg.articles:
                    if '第壹简报' in article.title:
                        self.friend.send(article.title)
                        self.friend.send(article.url)
                        #article_url = 'https://mp.weixin.qq.com/s/5E_SGRmaDA9O1nZgjGG0mw'
                        jb = jianbao.Get_Jianbao(article.url)
                        jb_content = jb.out_jianbao()
                        logger.info(jb_content)
                        self.friend.send(jb_content)
            if msg.type == SHARING and msg.sender.name == '硕士博士俱乐部':
                for article in msg.articles:
                    if '妹子篇' in article.title:
                        self.friend.send(article.title)
                        self.friend.send(article.url)
            if msg.type == SHARING and msg.sender.name == '硕博联谊':
                for article in msg.articles:
                    if  '妹子' in article.title and '现居北京' in article.title:
                        self.friend.send(article.title)
                        self.friend.send(article.url)
            """
            if msg.type == SHARING and msg.sender.name == '简报微刊':
                for article in msg.articles:
                    if '简报微刊' in article.title:
                        #self.friend.send(article.title)
                        #self.friend.send(article.url)
                        jb = jianbao.Get_Jianbao(article.url)
                        jb_content = jb.out_jianbao()
                        self.jb_content = jb_content
                        logger.info(jb_content)
                        #self.friend.send(jb_content)

                        for group_n in self.group_jianbao_list:
                            try:
                                my_group = self.bot.groups().search(group_n)[0]
                                my_group.send(jb_content)
                            except(IndexError,e):
                                logger.error('%s not exists, please check it!' %val)
            if msg.type == SHARING and msg.sender.name == '第壹简报':
                for article in msg.articles:
                    if '第壹简报' in article.title:
                        #self.friend.send(article.title)
                        #self.friend.send(article.url)
                        _jb = diyi.Get_Jianbao(article.url)
                        diyi_content = _jb.out_jianbao()
                        self.diyi_content = diyi_content
                        logger.info(diyi_content)
                        #self.friend.send(jb_content)

                        for group_n in self.group_jianbao_list:
                            try:
                                my_group = self.bot.groups().search(group_n)[0]
                                my_group.send(diyi_content)
                            except(IndexError,e):
                                logger.error('%s not exists, please check it!' %val)


    def msg_from_friends_accept(self):
        @self.bot.register(msg_types=FRIENDS)
        def auto_accept_friends(msg):
            logger.info("enter accept")
            #new_friend = self.bot.accept_friend(msg.card)
            new_friend = msg.card.accept()
            new_friend.send('嗨，您好！欢迎你加入芊芊结北京单身群，为了保证群内良好的交流与互动，请进群后务必根据群要求修改群名片，并完成相应步骤，你才能更好脱单哦！！')
            #msg.reply('欢迎加入北京芊芊结1群，加入更多群请回复：加群')
            #new_friend = self.bot.friends().search(msg.sender.name)[0]
            group_add = self.bot.groups().search(self.invite_group1)[0]
            group_add.add_members(new_friend, use_invitation=True)
            msg.reply_raw_msg(
            raw_type=42,
            raw_content='<msg username="ddyfy1991" nickname="豆豆要发芽"/>') 
            new_friend.send('另外如若想进入其他北京地区单身群，需要做点小任务哦！将以下图片转发到朋友圈，并配上以下\
文字，完成后将截图发送给我即可。文字内容如下：')
            new_friend.send(u"”这个平台不错哦，群主也很靠谱，大家可以扫描加入，体验一下“")
            new_friend.send_image("material/welcome.jpg")
            #logger.info("after accept")
            
    #处理群消息
    def group_msg(self):
        #注册消息
        @self.bot.register(Group)
        def print_msg(msg):
            #日志文件创建
            group_name = hashlib.md5(msg.sender.name.encode('utf-8')).hexdigest()[-8:]
            my_group = self.bot.groups().search(msg.sender.name)[0]
            log_file = os.path.join(self.path,group_name)
            #print group_name
            day = time.strftime("%Y-%m-%d")
            file_name = '%s.txt' % ( day)
            file_ab_path = os.path.join(log_file, file_name)
            #pic_file = 'log/%s-%s' % (group_zh_name,day)
            pic_file = os.path.join(self.path,group_name,day)
            if not os.path.exists(pic_file):
                os.mkdir(pic_file)
    
            create_time = msg.create_time.strftime('%Y-%m-%d %H:%M:%S')
            #name = msg.member.name
            name = msg.member.nick_name
            #群内有被at的消息就会智能回复，支持图灵和小i机器人，默认小i
            #print msg.is_at
            #print self.use_xiaoi
            #if msg.is_at and self.use_xiaoi == 1:
            myword = ''
            #消息处理，TEXT文本，SHARING链接，PICTURE图片，RECORDING语音，
            #ATTACHMENT附件，NOTE红包提示，新人入群提示，MAP地图
            #print PICTURE, VIDEO,RECORDING,ATTACHMENT
            if msg.type == TEXT:
                word = "%s %s:%s\n" % (create_time, name, msg.text)
                if msg.is_at or msg.text.startswith(u'小鱼儿'):
                    #tuling = Tuling(api_key=self.key)
                    ret_text, self.use_xiaoi = self.xiaoyuer.do_reply(msg,self.use_xiaoi,my_group)
              
                    #小豆机器人
                    if ret_text == '1' and self.use_xiaoi == 1:
                        ret_text = self.xiaodou.do_reply(msg)
                    if ret_text == '2' and self.use_xiaoi == 1:
                        ret_text = self.xiaoi.do_reply(msg)
                        #ret_text = tuling.do_reply(msg)
                    myword = "%s %s:%s\n" % (create_time, self.myself.name, ret_text)
                
            elif msg.type == SHARING:
                #print  msg
                word = "%s %s:SHARING:%s\n" % (create_time, name, msg.text)
                
            elif msg.type in [PICTURE, VIDEO,RECORDING,ATTACHMENT]:
                ct = msg.create_time.strftime('%Y-%m-%d-%H-%M-%S')
                if msg.type == PICTURE:
                    msg.get_file('%s/%s-%s-%s' % (pic_file,ct,random.randint(1,10),msg.file_name))
                    word = "%s %s:PICTURE:%s\n" % (create_time, name, msg.file_name)
                #elif msg.type == VIDEO:
                 #  msg.get_file('%s/%s-%s-%s' % (file_name,ct,name,msg.file_name))
                elif msg.type == RECORDING:
                    #print name
                    msg.get_file('%s/%s-%s-%s' % (pic_file,ct,name,msg.file_name))
                    word = "%s %s:RECORDING:%s\n" % (create_time, name, msg.file_name)
                elif msg.type == ATTACHMENT:
                    #print msg.file_name
                    msg.get_file('%s/%s-%s-%s' % (pic_file,ct,name,msg.file_name))
                    word = "%s %s:ATTACHMENT:%s\n" % (create_time, name, msg.file_name)
            elif msg.type == NOTE:
                #self.friend.send(word)
                if u'\u6536\u5230' in msg.text:
                    #print 'red packages!!!!!!!!!!!!!!!!!!!!!!'
                    self.friend.send('Red Package:%s' %(msg.sender.name))
                elif u'\u9080\u8bf7' in msg.text and self.newcomer == '1':
                    if group_name in self.group_newcomer_list: 
                        new_name = msg.text.split('"')[-2]
                        new_name_1 = None
                    elif group_name in self.group_newcomer_list1: 
                        #self.friend.send(self.group_newcomer_list1)
                        new_name_1 = msg.text.split('"')[-2]
                        new_name = None
                elif u'\u626b\u63cf' in msg.text and self.newcomer == '1':
                    if group_name in self.group_newcomer_list: 
                        new_name = msg.text.split('"')[1]
                        new_name_1 = None
                    elif group_name in self.group_newcomer_list1: 
                        new_name = None
                        new_name_1 = msg.text.split('"')[1]
                else:
                    new_name = new_name_1 = None
                
                if new_name:
                    #newcomer_msg = """@%s 欢迎新人进群交友聊天，请详细阅读群公告。\n进群请修改备注：昵称-出生年-性别-职业（学生）-学历，如：\n%s-90-男-IT-硕士"""% (new_name, new_name)
                    newcomer_msg = "@%s 欢迎新人入群！！"% (new_name) + "\n" + self.welcome_word
                    msg.reply(newcomer_msg)
                elif new_name_1:
                    newcomer_msg_1 = """@%s 欢迎进群，快来跟我聊天吧！！！"""% (new_name_1)
                    msg.reply(newcomer_msg_1)
                word = "%s %s:NOTE:%s\n" % (create_time, name, msg.text)
            elif msg.type == CARD:
                word = "%s %s:CARD:%s\n" % (create_time, name, msg.text)
            elif msg.type == MAP:
                word = "%s %s:MAP:%s\n" % (create_time, name, msg.text)
            elif msg.type == SYSTEM:
                word = "%s %s:SYSTEM:%s\n" % (create_time, name, msg.text)
    
            if word:
                with open(file_ab_path, "a+") as f:
                    f.write(word.encode('utf-8'))
                    if myword:
                        f.write(myword.encode('utf-8'))
                    word = None
            #msg.forward(self.friend)
    #记录日志
    def log_message(self,group_name, word):
        log_file = os.path.join(self.path,group_name)
        if not os.path.exists(log_file):
            os.mkdir(log_file)
        

        #日志文件创建
        day = time.strftime("%Y-%m-%d")
        file_name = '%s.txt' % ( day)
        file_ab_path = os.path.join(log_file, file_name)
        pic_file = os.path.join(self.path,group_name,day)
        if not os.path.exists(pic_file):
            os.mkdir(pic_file)
    
        with open(file_ab_path, "a+") as f:
            f.write(word.encode('utf-8'))
            word = None


    #每10分钟检测一次离群人员
    def send_message(self):
        #self.group_note_list  = [u'测试专用群']
        #print self.group_note_list
        for group_n in self.group_note_list:
            try:
                my_group = self.bot.groups().search(group_n)[0]
            except(IndexError,e):
                logger.error('%s not exists, please check it!' %group_n)
                continue

            #group_name = hashlib.md5(my_group.name.encode('utf-8')).hexdigest()[-8:]
            group_members = analyze.GroupMembers(self.path, my_group, self.friend) 
            group_members.analyze_mem()
        timer = threading.Timer(600, self.send_message)
        timer.start()

    #使用schedule模块执行定时任务
    def use_sche(self):
        #if self.send_me == 1:
        #self.send_message()
        #schedule.every().day.at("17:17").do(self.send_message)
        #schedule.every(10).minutes.do(self.send_message)
        schedule.every().day.at("08:00").do(self.send_friend_msg,self.send_morning)
        #schedule.every().day.at("22:30").do(self.send_friend_msg,self.send_night)
        #schedule.every().day.at("10:20").do(self.send_friend_msg,u"@all 休息一下吧，该喝水了！")
        #schedule.every().day.at("11:30").do(self.send_friend_msg,u"@all 该吃午饭了！")
        #schedule.every().day.at("13:00").do(self.send_friend_msg,u"@all 午休时间到！")
        #schedule.every().day.at("16:00").do(self.send_friend_msg,u"@all 休息一下吧，该喝水了！")
        
        while True:
            #self.myself.send('log out')
            if not self.bot.alive:
                logger.error('not login')
                self.main()
                break
            schedule.run_pending()
            time.sleep(10)
        

    #进入群聊接受消息 
    def run_task(self):            
        #if self.friends_accept:
            #self.msg_from_friends_accept()
        self.msg_from_friends()
        self.create_group_logfile()
        #my_groups = []
        self.group_msg()

        while True:
            if not self.bot.alive:
                logger.info('not login')
                self.main()
                break
            time.sleep(10)
        
        #embed()
        #self.bot.join()
            
    def main(self):
        self.login()
        #threads = []
        if self.recev_mps == 1:
            t1 = threading.Thread(target=self.my_mps,args=())
            t1.setDaemon(True)
            t1.start()

        #timer = threading.Timer(1, self.send_message)
        #timer.start()
        # send topic 
        #timer1 = threading.Timer(3600, self.send_group_msg)
        #timer1.start()
        t2 = threading.Thread(target=self.use_sche,args=())
        t2.setDaemon(True)
        t2.start()
        t3 = threading.Thread(target=self.run_task,args=())
        #t3.setDaemon(True)
        t3.start()

if __name__ == "__main__":
    group_m = GroupMessage()
    group_m.main()   


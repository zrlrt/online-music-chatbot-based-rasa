# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
#
from rasa_core.events import SlotSet
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
#
#
import datetime
import pymysql

class ActionLog(Action):

    def name(self) -> Text:
        return "action_check_user"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        db=database()
        num=tracker.get_slot("num")
        exist=db.check_user(num)
        if exist:
            name=db.search_name(num)
            dispatcher.utter_message(text="Hello "+str(name))
        else:
            dispatcher.utter_message(text="Your account does not exist,do you want to have a new account")
        db.db.close()
        return []

class ActionRegister(Action):

    def name(self) -> Text:
        return "action_register"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        db=database()
        name=tracker.get_slot("name")
        email=tracker.get_slot("email")
        num=db.register(name,email)
        db.db.close()
        dispatcher.utter_message(text="Congratulations on your successful registration. Your ID is "+str(num))

        return []

class ActionCheckMember(Action):

    def name(self) -> Text:
        return "action_check_member"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        db=database()
        num=tracker.get_slot("num")
        end=db.check_member(num)
        if end:
            dispatcher.utter_message(text=" Your membership will expire on "+end)
        else:
            dispatcher.utter_message(text="You haven't become a member yet")

        return []

class ActionCheckBalance(Action):

    def name(self) -> Text:
        return "action_check_balance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        db=database()
        num=tracker.get_slot("num")
        balance=db.balance(num)
        dispatcher.utter_message(text="Your balance is "+str(balance))
        return []

class ActionTopup(Action):

    def name(self) -> Text:
        return "action_top_up"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        db=database()
        num=tracker.get_slot("num")
        account=tracker.get_slot("account")
        balance=db.top_up(num,int(account))
        dispatcher.utter_message(text="Your balance is "+str(balance))
        return []

class ActionSearchMusic(Action):

    def name(self) -> Text:
        return "action_search_song"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        db=database()
        song=tracker.get_slot("music")
        url=db.searchSong(song)
        dispatcher.utter_message(text=url)
        return []

class ActionSearchSinger(Action):

    def name(self) -> Text:
        return "action_search_singer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        db=database()
        singer=tracker.get_slot("singer")
        songs=db.searchSinger(singer)
        dispatcher.utter_message(text=songs)
        return []

class Actioncollect(Action):

    def name(self) -> Text:
        return "action_collect"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        db=database()
        num=tracker.get_slot("num")
        song=tracker.get_slot("song")
        db.collection(num,song)
        dispatcher.utter_message(text="you have collected successfully")
        return []

class ActionCheckCollect(Action):

    def name(self) -> Text:
        return "action_check_collect"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        db=database()
        num=tracker.get_slot("num")
        songs=db.checkcollection(num)
        dispatcher.utter_message(text=songs)
        return []

class ActionGetMember(Action):

    def name(self) -> Text:
        return "action_get_member"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        db=database()
        num=tracker.get_slot("num")
        time=tracker.get_slot("time")
        i=0
        if 'one month' in time:
           i=1
        elif 'half' or 'six months' in time:
            i=2
        elif 'one' or 'a' and 'year' in time:
            i=3
        elif 'five' in time:
            i=4
        get=db.member(num,i)
        if get:
            dispatcher.utter_message(text="You have successfully opened your membership")
        else:
            dispatcher.utter_message(text="Failed to identify, please re-enter")
        return []

class database():
    def __init__(self):
        self.db=self.connect()
        self.cursor=self.db.cursor()

    def connect(self):
        db=pymysql.connect(
            host='rm-d7or6r080xof7tf1w2o.mysql.eu-west-1.rds.aliyuncs.com',
            user='root',
            password='zrl004200',
            database='chatbot'
        )
        return db

    def check_user(self,num):
        str1="select user_num from user where user_num=%s"
        self.cursor.execute(str1%(num))
        if self.cursor.fetchone():
            return True
        else:
            return False

    def search_name(self,num):
        sql="select user_name from user where user_num=%s"
        self.cursor.execute(sql%(num))
        name=self.cursor.fetchone()[0]
        return name

    def check_member(self,num):
        str1="select over_time from user where user_num=%s"
        self.cursor.execute(str1%(num))
        time=self.cursor.fetchone()
        end=time[0]
        if end:
            back=" Your membership will expire on "+end
            return back
        else:
            print("You haven't become a member yet")

    def register(self,name,mail):
        str1="INSERT INTO user set user_name='%s',user_email='%s'"
        self.cursor.execute(str1%(name,mail))
        num=10000
        str_num="select user_num from user"
        self.cursor.execute(str_num)
        self.db.commit()
        nums=self.cursor.fetchall()
        for r in nums:
            if r[0]>num:
                num=r[0]
        return num

    def balance(self,num):
        str1="select user_balance from user where user_num=%s"
        self.cursor.execute(str1%(num))
        balance=self.cursor.fetchone()[0]
        return balance

    def getTime(self):
        time=datetime.datetime.now()
        str_time="%s-%s-%s"%(time.year,time.month,time.day)
        return str_time

    def getEnd(self,d):
        t=datetime.datetime.now()
        end=(t+datetime.timedelta(days=d)).strftime("%Y-%m-%d")
        return end

    def member(self,num,i):
        balance=self.balance(num)
        now=""
        end=""
        done=False
        if i==1 :
            if balance>15:
                now=self.getTime()
                end=self.getEnd(30)
                balance=balance-15
                done=True
        elif i==2 :
            if balance>88:
                now=self.getTime()
                end=self.getEnd(180)
                balance=balance-88
                done=True
        elif i==3 :
            if balance>158:
                now=self.getTime()
                end=self.getEnd(365)
                balance=balance-158
                done=True
        elif i==4 :
            if balance>690:
                now=self.getTime()
                end=self.getEnd(1825)
                balance=balance-690
                done=True
        else:
            pass
        if done:
            sql="update user set member_time='%s',over_time='%s',user_balance=%d,user_member=1 where user_num=%s"%(now,end,balance,num)
            self.cursor.execute(sql)
            self.db.commit()
        return done

    def free(self,num):
        sql="update user set user.user_try=0 where user_num=%s"
        self.cursor.execute(sql%(num))
        self.db.commit()

    def searchSong(self,name):
        sql="select song_url from songs where song_name='%s'"
        self.cursor.execute(sql%(name))
        u=self.cursor.fetchone()
        if u:
            url=u[0]
        else:
            url="I'm sorry we don't have the copyright on this song"
        return url

    def searchSinger(self,name):
        sql="select song_name,song_url from songs where song_singer='%s'"
        self.cursor.execute(sql%(name))
        s=self.cursor.fetchall()
        songs=''
        if s:
            for song in s:
                songs="the url of "+song[0]+" is "+song[1]
        else:
            songs="I'm sorry I couldn't find the singer"
        return songs

    def top_up(self,num,account):
        balance=self.balance(num)
        balance=balance+account
        sql="update user set user_balance=%d where user_num=%s"
        self.cursor.execute(sql%(balance,num))
        self.db.commit()
        return balance

    def collection(self,num,song):
        sql1="select song_num fron songs where song_name='%s'"
        self.cursor.execute(sql1%(song))
        song_num=self.cursor.fetchone()[0]
        sql2="INSERT INTO collection set user_num=%s,song_num=%s"
        self.cursor.execute(sql2%(num,song_num))
        self.db.commit()

    def checkcollection(self,num):
        sql="select song_name,song_singer from songs where song_num in (select song_num from collection where user_num=%s)"
        self.cursor.execute(sql%(num))
        songs=""
        results=self.cursor.fetchall()
        if results:
            for r in results:
                songs=songs+r[0]+':  '+r[1]
        else:
            songs="You don't have any songs in your collection"
        return songs


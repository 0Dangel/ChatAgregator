from array import array
from asyncio.windows_events import NULL
from ctypes import WinError
from multiprocessing.connection import wait
from queue import Empty
import time

import json
from logging import exception, handlers
#from msilib.schema import Class
from posixpath import dirname

from threading import Thread
#from aiohttp import worker
from async_timeout import asyncio
from tornado.ioloop import IOLoop
import tornado
import sqlite3
from os import path
import os
import pytchat
import json
import tornado.ioloop
import tornado.web
import asyncio
from os.path import dirname
from tornado.web import StaticFileHandler
from tornado.websocket import WebSocketHandler
import socket, time
import asyncio
import multiprocessing as mp 
from multiprocessing import Queue


tornado.ioloop.IOLoop.configure("tornado.platform.asyncio.AsyncIOLoop")
io_loop = tornado.ioloop.IOLoop.current()
asyncio.set_event_loop(io_loop.asyncio_loop)

#ws_clients = []


class WebServer(tornado.web.Application):
   
    iol = IOLoop.current()
    tohle = ""
    ws_clients = []
    
    def __init__(self):
        
        global tohle
        tohle = self
        handlers = [
             (r"/", MainHandler),
             (r"/websocket",WSHandler,{"app":self}),
             (r'/(.*)', StaticFileHandler, {'path': dirname(__file__)})
             ]
        settings = {'debug':True}
        self.listen(8080)
        tornado.web.Application.__init__(self,handlers, **settings)
                
    def send_ws_message(self, message):
        for client in self.ws_clients:
            iol.spawn_callback(client.write_message, message)


        #print(len(self.ws_clients))


class AuthHandler():
    def on_message(self,msg):
        print(msg)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #self.write("Hello, world")
        self.render("main.html")

class WSHandler(WebSocketHandler):

    def initialize(self, app):
        self.app = app
        self.app.ws_clients.append(self)

    def open(self):
        print('Webserver: Websocket opened.')
        self.write_message('Server ready.')

    def on_message(self, msg):
        print('Webserver: Received WS message:', msg)

    def on_close(self):
        self.application.ws_clients.remove(self)
        print('Webserver: Websocket client closed. Connected clients:', len(self.application.ws_clients))

class Twitch_chat():
    sock = socket.socket()
    server = ""
    errCount = 0


    def  __init__(self,channel : str):
        
        
        self.server = channel
        self.connect()
        # self.sock.connect(('irc.chat.twitch.tv',6667))
        # self.sock.send(f"PASS oauth:d5kk5jf7fzeuz6fux5ykf9os9azveu\n".encode('utf-8'))
        # self.sock.send(f"NICK 0dangel\n".encode('utf-8'))
        # self.sock.send(f"CAP REQ : twitch.tv/tags\n".encode('utf-8'))
        # self.sock.send(f"JOIN {channel}\n".encode('utf-8'))    
        # #self.sock.setblocking(False)
        # #self.sock.settimeout(0.1)
        # print("Nastaveno:" , channel)


    def parseChat(self,resp:str) -> array:
        resp = resp.rstrip().split('\r\n')
        result = []
        for line in resp:            
            if "PRIVMSG" in line:
                #print(line)
                
                #print("")
                line_split = line.split(';')
                param_dict = {}
               
                for param in line_split:
                    semi = param.split('=',1)
                    param_dict[str(semi[0])] = semi[1]

                msg = param_dict["user-type"].split(':')[-1]
                result.append({"userID":param_dict["user-id"],"user":param_dict["display-name"],"message":msg,"mod":bool(int(param_dict["mod"])),"sponsor":bool(int(param_dict["subscriber"])),"owner":param_dict["user-id"]==param_dict["room-id"],"platform":"twitch","verified":("verified" in param_dict["badges"])})

        return result


    def readChat(self) -> array:
            #print(self.server)
        #try:
            resp = self.sock.recv(2048).decode('utf-8')
            #print(resp)
            if(resp.startswith("PING")):
                self.sock.send("PONG\n".encode('utf-8'))
            elif len(resp) > 0:
                if(len is not None):
                    return self.parseChat(resp)

    def connect(self) -> None:
        try:
            self.sock.connect(('irc.chat.twitch.tv',6667))
            self.sock.send(f"PASS {self.OAUTH}\n".encode('utf-8'))
            self.sock.send(f"NICK {self.nick}\n".encode('utf-8'))
            self.sock.send(f"CAP REQ : twitch.tv/tags\n".encode('utf-8'))
            self.sock.send(f"JOIN {self.server}\n".encode('utf-8'))    
            self.errCount =0
        except ConnectionResetError:
            time.sleep(pow(2,self.errCount))
            print("Connection refused by server - probabbly 'spam' reasons... Retry in: 2^", self.errCount," seconds")            
            if(self.errCount < 5):
                self.errCount += 1


    def main(self,queue : Queue) -> None:
        self.connect()
                       
        #self.sock.setblocking(False)
        #self.sock.settimeout(0.1)
        while(True):
            queue.put(self.readChat())
        


       


class YT_Chat():
    #So far only for YT Chat - TODO: Add a Twitch implementation too - Preferably using same way as PytChat uses for YouTube ?(Screw Twitch API)?
    
    TwitchChat= None
    DB_Sqlite = None
    viewers = {}
    TwitchQueue = None
    

    def  __init__(self,vidID:str, twitchAcc:str)-> None:
        self.chat = pytchat.create(video_id=vidID)
        self.TwitchQueue= mp.Queue()
        print(self.TwitchQueue)
        self.TwitchChat = mp.Process(target = Twitch_chat.main, args=(Twitch_chat(twitchAcc),self.TwitchQueue))
        #message(json.loads(self.chat.get().json()))
        
        #self.chat.get().
        
        db_File_name = "viewers_temp.sqlite"
        

        if(not path.exists(db_File_name)):
           self.DB_Sqlite= sqlite3.connect(db_File_name)
           self.DB_Sqlite.execute("CREATE TABLE \"viewers\" (	\"id\"	STRING NOT NULL,	\"Name\"	TEXT,	\"Points\"	INTEGER DEFAULT 0,	\"Stream_count\"	INTEGER DEFAULT 0,	\"Message_count\"	INTEGER DEFAULT 0,	\"Donos\"	INTEGER DEFAULT 0,	\"Type\"	INTEGER,	\"FirstMessage_date\"	BLOB DEFAULT CURRENT_TIMESTAMP,	PRIMARY KEY(\"id\")               )")


        if(not self.DB_Sqlite):
            self.DB_Sqlite = sqlite3.connect(db_File_name)
        db_cursor = self.DB_Sqlite.cursor()

    def database(self,command:str, data:array)->None:
        
        return

    def chat_command(user: str,message: str) -> None:
        return


    def main_function(self):
       
        print("After Server")
        self.TwitchChat.start()
        
        while(True):
            try:
                result=self.TwitchQueue.get_nowait()
                ws.send_ws_message(message=json.dumps(result))
            except Empty:
                pass
            #result = self.TwtcChat.readChat()
            #print(time.time()-now,"   Twitch Fetch")

            data = self.chat.get()
            # print(time.time()-now,"   Youtube Fetch")

            # print(time.time()-now)
            ytArr = []
            if(data != None and data != NULL):
                for c in data.sync_items() :
                    jsonized =json.loads( c.json())
                    #print(jsonized)
                    #print(jsonized["author"]["name"] + ":   " + jsonized["message"])
                    userID = jsonized["author"]["channelId"]
                    user_name = jsonized["author"]["name"]
                    ytArr.append({"platform":"yt","user":user_name,"userID":userID,"owner":jsonized["author"]["isChatOwner"],"sponsor":jsonized["author"]["isChatSponsor"],"mod":jsonized["author"]["isChatModerator"],"verified":jsonized["author"]["isVerified"],"message": jsonized["message"],"amount":jsonized["amountValue"],"currency": jsonized["currency"], "image":jsonized["author"]["imageUrl"].replace("yt4.ggpht","yt3.ggpht"),"badgeUrl":jsonized["author"]["badgeUrl"]})
            if(len(ytArr)>0):    
                ws.send_ws_message(message=json.dumps(ytArr))
            # print(time.time()-now)
            #print("")
            now = time.time()
        return

       # try:
        #SQL_Queue_insert = []
        #SQL_Queue_update = []
        # SQL_Queue = []
        # SQL_Queue.append("BEGIN TRANSACTION;")
        
        # last_DB_update = time.time()
        # while(True):
        #     data = self.chat.get()
        #     for c in data.sync_items():
        #         jsonized =json.loads( c.json())
        #         #print(jsonized)
        #         #print(jsonized["author"]["name"] + ":   " + jsonized["message"])
        #         userID = jsonized["author"]["channelId"]
        #         user_name = jsonized["author"]["name"]
        #         if(str(jsonized["message"]).startswith("!") ):
        #            chat_command(user_name, str(jsonized["message"]))

        #         ws.send_ws_message(message=json.dumps({"platform":"yt","user":user_name,"userID":userID,"user_own":jsonized["author"]["isChatOwner"],"user_spo":jsonized["author"]["isChatSponsor"],"user_mod":jsonized["author"]["isChatModerator"],"user_ver":jsonized["author"]["isVerified"],"msg": jsonized["message"],"amount":jsonized["amountValue"],"currency": jsonized["currency"], "image":jsonized["author"]["imageUrl"].replace("yt4.ggpht","yt3.ggpht"),"badgeUrl":jsonized["author"]["badgeUrl"]}))
        #         #Websocket rendering is to be done using JScript -> one of many reasons why we actually host local webserver so that the visual aspects can be "easily modified using JScript and such... Screw PyQt5"
        #         if(userID not in self.viewers):
        #             self.viewers[userID] = True
        #          #   Might be good to implement some kind of multiplier for Members ? - TODO
        #             SQL_Queue.append("insert or ignore into viewers (ID,Name)VALUES (\""+userID+"\",\""+user_name+"\");")
        #             SQL_Queue.append("update or IGNORE viewers set Message_count = Message_count +1, Stream_count = Stream_count+1, Donos = Donos + "+str(jsonized["amountValue"])+"  where ID = \""+userID+"\";")   
        #           #  TODO: Change how this works - use "ExecuteMany with a parameter rather than saving the whole damn commands"
        #         else:
        #             SQL_Queue.append("update or IGNORE viewers set Message_count = Message_count +1, Donos = Donos + "+str(jsonized["amountValue"])+"  where ID = \""+userID+"\";")    
            
            
        #     if((time.time() - last_DB_update) >= 10 ):
        #         for i in self.viewers:
        #             SQL_Queue.append("update or IGNORE viewers set Points = Points + 100 where ID = \""+i+"\";")
        #         SQL_Queue.append("COMMIT;")

        #         if(len(SQL_Queue) > 2):
        #             self.DB_Sqlite.executescript(" ".join(SQL_Queue))
        #         SQL_Queue.clear()
        #         SQL_Queue.append("BEGIN TRANSACTION;")
        #         last_DB_update = time.time()

        # # while(True):
        # #     Twitch_chat.readChat(Twitch_chat)



        #except:
         #   return("I failed")

 



#"{\"author\": {\"badgeUrl\": \"\", \"type\": \"\", \"isVerified\": false, \"isChatOwner\": false, \"isChatSponsor\": false, \"isChatModerator\": false, \"channelId\": \"UCWld8VohnjT0TLxhNcVelkQ\", \"channelUrl\": \"http://www.youtube.com/channel/UCWld8VohnjT0TLxhNcVelkQ\", \"name\": \"ABCD\", \"imageUrl\": \"https://yt4.ggpht.com/ytc/AKedOLRvlvZKIkRXFbUzy8eM-SJjJ97gl2bUoYCgUhNIOOukc02hYoVfQh8WiQO5Rsu9=s64-c-k-c0x00ffffff-no-rj\"}, \"type\": \"textMessage\", \"id\": \"CkUKGkNJSElnZnVRel9VQ0ZTTU1mUW9kcTNNTVZREidDTG5DaVphUXpfVUNGV1NBNWdvZF9QOEc0dzE2NDMxOTAzMTg3MTI%3D\", \"timestamp\": 1643190320915, \"elapsedTime\": \"\", \"datetime\": \"2022-01-26 10:45:20\", \"message\": \"@Alam Khan :thinking_face:India pasand nhi to Pakistan jao:thumbs_up: Afghanistan jao,, koi nhi rok raha:smiling_face_with_sunglasses:\", \"messageEx\": [\"@Alam Khan \", {\"id\": \"🤔\", \"txt\": \":thinking_face:\", \"url\": \"https://www.youtube.com/s/gaming/emoji/828cb648/emoji_u1f914.svg\"}, \"India pasand nhi to Pakistan jao\", {\"id\": \"👍\", \"txt\": \":thumbs_up:\", \"url\": \"https://www.youtube.com/s/gaming/emoji/828cb648/emoji_u1f44d.svg\"}, \" Afghanistan jao,, koi nhi rok raha\", {\"id\": \"😎\", \"txt\": \":smiling_face_with_sunglasses:\", \"url\": \"https://www.youtube.com/s/gaming/emoji/828cb648/emoji_u1f60e.svg\"}], \"amountValue\": 0.0, \"amountString\": \"\", \"currency\": \"\", \"bgColor\": 0}"


def start_server():
    asyncio.set_event_loop(asyncio.new_event_loop())
    ws.run()

#worker.broadcast = Broadcast
 
if __name__ == "__main__":
    print(str(os.getcwd()))
    ws = WebServer()
    #t = Thread(target = start_server,args=())
    #t.start()
    settingFile = ""
    with open("./env/settings.json") as set_file :        
        try:
            #print(set_file.readlines())
            settingFile = json.load(set_file)
        except Exception as exc:
            print("Unexpected error occured, 'Chat Agregator' has been terminated")
            print(exc)
            exit()    

    video_id = settingFile["ytVideo"]
    reader = YT_Chat(vidID= video_id, twitchAcc= settingFile["TwitchAcc"])

    t = Thread(target=reader.main_function,daemon=True)
    t.start()
  
 
    iol = IOLoop.current()
    iol.start()


    print("Err: How did I get here?!")
    t.join()

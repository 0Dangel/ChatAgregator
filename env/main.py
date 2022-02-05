from ast import arg
from datetime import datetime
from distutils import command
from email import message
import time

import json
from logging import exception, handlers
from msilib.schema import Class
from posixpath import dirname

from threading import Thread
from urllib import request

#from aiohttp import worker
from async_timeout import asyncio
from tornado.ioloop import IOLoop
import tornado
import sqlite3
from os import path



import pytchat
from pytchat import LiveChat
import json

import tornado.ioloop
import tornado.web
import websockets
import asyncio


from os.path import dirname

from tornado.web import StaticFileHandler

from tornado.websocket import WebSocketHandler



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
             (r'/(.*.js)', StaticFileHandler, {'path': dirname(__file__)}),
             (r'/auth',AuthHandler,)
             ]
        settings = {'debug':True}
        self.listen(8080)
        tornado.web.Application.__init__(self,handlers, **settings)
        




        
    def send_ws_message(self, message):
        for client in self.ws_clients:
            try:
                iol.spawn_callback(client.write_message, message)
            except:
                iol.spawn_callback(client.write_message, json.dumps(message))

        #for client in self.ws_clients:
         #   try:
          #      self.iol.spawn_callback(client.write_message, message)
           # except:
            #    self.iol.spawn_callback(client.write_message, json.dumps(message))
        
        #tohle.write_message("message")
        #print("yes")
        print(len(self.ws_clients))



#def bcint(message):
    #print("-------")
 #   print(len(ws_clients))
  #  for client in ws_clients:
   #     client.write_message(message)
 #       print(message)
#
#def Broadcast(message):
#    io_loop.asyncio_loop.call_soon_threadsafe(bcint,message)

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
        #self.app.send_ws_message(message="This doesn't work")
        #self.application.ws_clients.append(self)

    def on_message(self, msg):
        print('Webserver: Received WS message:', msg)

    def on_close(self):
        self.application.ws_clients.remove(self)
        print('Webserver: Websocket client closed. Connected clients:', len(self.application.ws_clients))


class YT_Chat():
    #So far only for YT Chat - TODO: Add a Twitch implementation too - Preferably using same way as PytChat uses for YouTube ?(Screw Twitch API)?
    
    chat = None

    


    def  __init__(self,vidID):
        self.chat = pytchat.create(video_id=vidID)
        #message(json.loads(self.chat.get().json()))
        chat = self.chat.get()
        #self.chat.get().

        


    def main_function(self):

        DB_Sqlite = None
        db_File_name = "viewers_temp.sqlite"
        viewers = {}

        if(not path.exists(db_File_name)):
           DB_Sqlite= sqlite3.connect(db_File_name)
           DB_Sqlite.execute("CREATE TABLE \"viewers\" (	\"id\"	STRING NOT NULL,	\"Name\"	TEXT,	\"Points\"	INTEGER DEFAULT 0,	\"Stream_count\"	INTEGER DEFAULT 0,	\"Message_count\"	INTEGER DEFAULT 0,	\"Donos\"	INTEGER DEFAULT 0,	\"Type\"	INTEGER,	\"FirstMessage_date\"	BLOB DEFAULT CURRENT_TIMESTAMP,	PRIMARY KEY(\"id\")               )")


        if(not DB_Sqlite):
            DB_Sqlite = sqlite3.connect(db_File_name)


        print("After Server")
       # try:
        SQL_Queue = []
        SQL_Queue.append("BEGIN TRANSACTION;")
        last_DB_update = time.time()
        while(True):
            data = self.chat.get()
            for c in data.sync_items():
                jsonized =json.loads( c.json())
                #print(jsonized["author"]["name"] + ":   " + jsonized["message"])
                userID = jsonized["author"]["channelId"]
                user_name = jsonized["author"]["name"]
                if(str(jsonized["message"]).startswith("!") ):
                    command(user_name, jsonized["message"])
                ws.send_ws_message(message=json.dumps({"platform":"yt","user":user_name,"userID":userID,"msg": jsonized["message"],"amount":jsonized["amountValue"],"currency": jsonized["currency"], "image":jsonized["author"]["imageUrl"].replace("yt4.ggpht","yt3.ggpht"),"badgeUrl":jsonized["author"]["badgeUrl"]}))
                #Websocket rendering is to be done using JScript -> one of many reasons why we actually host local webserver so that the visual aspects can be "easily modified using JScript and such... Screw PyQt5"
                if(userID not in viewers):
                    viewers[userID] = True
                    #Might be good to implement some kind of multiplier for Members ? - TODO
                    SQL_Queue.append("insert or ignore into viewers (ID,Name)VALUES (\""+userID+"\",\""+user_name+"\");")
                    SQL_Queue.append("update or IGNORE viewers set Message_count = Message_count +1, Stream_count = Stream_count+1, Donos = Donos + "+str(jsonized["amountValue"])+"  where ID = \""+userID+"\";")   
                    #TODO: Change how this works - use "ExecuteMany with a parameter rather than saving the whole damn commands"
                else:
                    SQL_Queue.append("update or IGNORE viewers set Message_count = Message_count +1, Donos = Donos + "+str(jsonized["amountValue"])+"  where ID = \""+userID+"\";")    
            if((time.time() - last_DB_update) >= 10 ):
                for i in viewers:
                    SQL_Queue.append("update or IGNORE viewers set Points = Points + 100 where ID = \""+i+"\";")
                SQL_Queue.append("COMMIT;")

                if(len(SQL_Queue) > 2):
                    DB_Sqlite.executescript(" ".join(SQL_Queue))
                SQL_Queue.clear()
                SQL_Queue.append("BEGIN TRANSACTION;")
                last_DB_update = time.time()



                    # Here goes SQL update or ignore

                    #if(self.viewers[jsonized["author"]["channelId"]]):
                     #   print("jkek")
                    #self.DB_Sqlite.execute()
                    #ws.send_ws_message(message=c.json())
                    #SQL Commands to use:
                    #insert or ignore into viewers (ID,Name)VALUES ("UCQ5M_FnD7NpuLc3e5zjlBkg","ALT");
                    #update or IGNORE viewers set Message_count = Message_count +1, Name = "+jsonized["author"]["name"]+", Stream_count = Stream_count+1 where ID = jsonized["author"]["channelId"]

        #except:
         #   return("I failed")

    def command(user: str,message: str) -> None:
        return



#"{\"author\": {\"badgeUrl\": \"\", \"type\": \"\", \"isVerified\": false, \"isChatOwner\": false, \"isChatSponsor\": false, \"isChatModerator\": false, \"channelId\": \"UCWld8VohnjT0TLxhNcVelkQ\", \"channelUrl\": \"http://www.youtube.com/channel/UCWld8VohnjT0TLxhNcVelkQ\", \"name\": \"ABCD\", \"imageUrl\": \"https://yt4.ggpht.com/ytc/AKedOLRvlvZKIkRXFbUzy8eM-SJjJ97gl2bUoYCgUhNIOOukc02hYoVfQh8WiQO5Rsu9=s64-c-k-c0x00ffffff-no-rj\"}, \"type\": \"textMessage\", \"id\": \"CkUKGkNJSElnZnVRel9VQ0ZTTU1mUW9kcTNNTVZREidDTG5DaVphUXpfVUNGV1NBNWdvZF9QOEc0dzE2NDMxOTAzMTg3MTI%3D\", \"timestamp\": 1643190320915, \"elapsedTime\": \"\", \"datetime\": \"2022-01-26 10:45:20\", \"message\": \"@Alam Khan :thinking_face:India pasand nhi to Pakistan jao:thumbs_up: Afghanistan jao,, koi nhi rok raha:smiling_face_with_sunglasses:\", \"messageEx\": [\"@Alam Khan \", {\"id\": \"🤔\", \"txt\": \":thinking_face:\", \"url\": \"https://www.youtube.com/s/gaming/emoji/828cb648/emoji_u1f914.svg\"}, \"India pasand nhi to Pakistan jao\", {\"id\": \"👍\", \"txt\": \":thumbs_up:\", \"url\": \"https://www.youtube.com/s/gaming/emoji/828cb648/emoji_u1f44d.svg\"}, \" Afghanistan jao,, koi nhi rok raha\", {\"id\": \"😎\", \"txt\": \":smiling_face_with_sunglasses:\", \"url\": \"https://www.youtube.com/s/gaming/emoji/828cb648/emoji_u1f60e.svg\"}], \"amountValue\": 0.0, \"amountString\": \"\", \"currency\": \"\", \"bgColor\": 0}"


def start_server():
    asyncio.set_event_loop(asyncio.new_event_loop())
    ws.run()

#worker.broadcast = Broadcast
 
if __name__ == "__main__":
    ws = WebServer()
    #t = Thread(target = start_server,args=())
    #t.start()
    settingFile = ""
    with open("env\settings.json") as set_file :        
        try:
            #print(set_file.readlines())
            settingFile = json.load(set_file)
        except Exception as exc:
            print("Unexpected error occured, 'Chat Agregator' has been terminated")
            print(exc)
            exit()    

    video_id = settingFile["ytVideo"]
    reader = YT_Chat(vidID= video_id)

    t = Thread(target=reader.main_function,daemon=True)
    t.start()
  
 
    iol = IOLoop.current()
    iol.start()
            #t.app.send_ws_message(message="Nope")
            #
            #ws.application.send_message("Prdel")
            #ws.send_ws_message("prdel")
            #print(jsonized)

    print("Err: How did I get here?!")
    t.join()

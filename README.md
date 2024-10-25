This project started as a solution to a problem I encountered while streaming to multiple platforms.

The problem:
When you stream on multiple platforms using your own way of stream distribution e.g. locally running nginx, you don't have access to tools that are provided by usual agregation platforms (like ReStream)
I needed to read both chats to engage with viewers and the only easy solution for me was to have 2 or more windows with chat opened.

Thus I created a solution to my own problem.

This Python powered app creates local webserver using Tornado which provides its service on the port 8080.

After loading this page, client connects to the webserver using Websocket protocol which is later used for message transportation.

In the mean time in another thread the app scrapes messages from provided channels / urls.
Parses messages depending on their source, repacks them into a much simplier format that gets send through websocket connections to every connected browser.
This allows you to add a chat feed into a stream video using a "browser source" in OBS while also having a normal, one window of browser open specifically for chat.
Parsed messages get also used for statistics keeping, each user is added to local SQLite database and his other statistics get tracked like:
- date of first message is recorded
- number of joined streams
- total amount donated
- and others  

In current state there is no "easy" way of changing the design of messages.
Current design discerns between "paid users" - Youtube Supporters / Twitch subscribers, normal users, verified users, Moderators and chat Owner.

There are a lot of different problems, solving these would make this program much more usable.
Also there is soo much room for improvements, adding a chatbot-like capabilities, auto-modding, game integrations and others are functions yet to be added.

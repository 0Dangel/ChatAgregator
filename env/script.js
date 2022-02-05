var alldata

function onSocketOpen() {
    console.log("WS client: Websocket opened.")
}

function onBodyLoad() {
    ws = new WebSocket('ws://localhost:8080/websocket');     // ws is a global variable (index.html)
    ws.onopen = onSocketOpen;
    ws.onmessage = onSocketMessage;
    ws.onclose = onSocketClose;
    //setInterval(fn60sec, 120 * 1000);
    

}



function onSocketMessage(message) {
        console.log("WS message: ", message)

try {
        data = JSON.parse(message.data)
	document.write(data.user + ":" + data.msg+"<br>");
    } catch (e) {
        //data = message.data
	data = ""
    }
    

	

    
}

function getMessage(data){
	if(!data.hasOwnProperty("message"))
	{ return 'x'}
	return +data["name"]


}

function onSocketClose() {
    console.log("WS client: Websocket closed.")
}
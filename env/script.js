var alldata;
var comments;
var mainRow 

function onSocketOpen() {
    console.log("WS client: Websocket opened.")
}

function onBodyLoad() {
    ws = new WebSocket('ws://localhost:8080/websocket');     // ws is a global variable (index.html)
    ws.onopen = onSocketOpen;
    ws.onmessage = onSocketMessage;
    ws.onclose = onSocketClose;
    document.write('<head><script src = "./js/bootstrap.js"> </script>     <link rel="stylesheet" href="./css/bootstrap.css">    <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1">   <meta name="description" content="">   <script src="script.js" type="text/javascript"></script> </head>');
    document.write(" <div  class = 'container' id = 'MainRows'>  </div> ");
    //setInterval(fn60sec, 120 * 1000);
    mainRow=document.getElementById("MainRows");

}



function onSocketMessage(message) {
        console.log("WS message: ", message)

try {
    data = JSON.parse(message.data);

    //comments.push(message.data);
    //if(comments.lenght > 20)
    //{
      //  comments.shift();

    //}
    
    


    mainRow.innerHTML += "<div class='row' style = 'padding-top: 3px ;box-shadow: 0 0px 0px 0 rgba(0,0,0,0.4) 0 5px 8px 0 rgba(0,0,0,0.4); background-color: #FAA800'> <div class = 'col-sm-4' style = 'border-width: 1px; border-style: solid; border-color:#000000 '>"+data.user +'</div>'+ '<div class = "col-sm-8 ">    ' + data.msg+'</div>  </div> '   ; 
    
    
    //document.write(data.user + ":" + data.msg+"<br>");
    window.scrollTo(0, window.innerHeight);

    } catch (e) {
        //data = message.data
	data = "";
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
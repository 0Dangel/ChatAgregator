var alldata;
var comments;
var mainRow ;
var countRows = 0;
var deletingRows = false;

function onSocketOpen() {
    console.log("WS client: Websocket opened.")
}

function onBodyLoad() {
    ws = new WebSocket('ws://localhost:8080/websocket');     // ws is a global variable (index.html)
    ws.onopen = onSocketOpen;
    ws.onmessage = onSocketMessage;
    ws.onclose = onSocketClose;
    document.write('<head><script src = "./js/bootstrap.js"> </script>     <link rel="stylesheet" href="./css/bootstrap.css">    <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1">   <meta name="description" content="">   <script src="script.js" type="text/javascript"></script> </head>');
    document.write(" <div  class = 'container' style='font-size:3px' id = 'MainRows'>  </div> ");
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
    
    

 //style = 'background-color: #FAA800'
    nameColor = "FFFFFF"
    switch(data.platform)
    {
        case "yt":
            nameColor = "AA0000";
            break;
        case "twitch":
            nameColor = "AA00AA";
            break;
    }
    badgeImg=""

    if(data.user_spo)
    {
        //badgeImg+="sponsor "
        badgeImg += '<img src='+data.badgeUrl +' alt="">';
        nameColor = "00AA00"
    }
    if(data.user_ver)
    {
        badgeImg+="verified "
        //badgeImg = '<img src='+data.badgeURL +' alt="">';
    }
    if(data.user_mod)
    {
        badgeImg+="mod "
        //badgeImg = '<img src='+data.badgeURL +' alt="">';
        nameColor = "FFA800"
    }
    if(data.user_own)
    {
        badgeImg+="owner "
        //badgeImg = '<img src='+data.badgeURL +' alt="">';
    }




    
    mainRow.innerHTML += "<div class='row' id="+countRows+"  style = 'background-color: rgba(0,0,0,0.5)'> <div class = 'col-sm-3' style = 'font-weight: bold; color:#"+nameColor+"'>"+badgeImg +"::" +data.user +'</div>'+ '<div class = "col-sm-9" style="color = #FFFFFF; font-weight: bolder">    ' + data.msg+'</div>  </div> <br>'   ; 
    countRows +=1;
    if(countRows > 15)
    {       
        countRows = 0;
        deletingRows = true;
        
    }

    if(deletingRows)
    {
        mainRow.firstElementChild.remove();
        mainRow.firstElementChild.remove();

    }
    
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
    ws = new WebSocket('ws://localhost:8080/websocket');     // ws is a global variable (index.html)
    ws.onopen = onSocketOpen;
    ws.onmessage = onSocketMessage;
    ws.onclose = onSocketClose;
}
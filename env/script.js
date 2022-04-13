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

try {JSON.parse(message.data).forEach(element => {
    //data = JSON.parse(message.data);

    //comments.push(message.data);
    //if(comments.lenght > 20)
    //{
      //  comments.shift();

    //}
    
    

 //style = 'background-color: #FAA800'
    nameColor = "FFFFFF"
    switch(element.platform)
    {
        case "yt":
            nameColor = "AA0000";
            break;
        case "twitch":
            nameColor = "AA00AA";
            break;
    }
    badgeImg=""

    if(element.sponsor)
    {
        if(element.badgeUrl != null){
            badgeImg += '<img src='+element.badgeUrl +' alt="">';}
        else{
            badgeImg += 'sponsor';}
        nameColor = "00AA00";
    }
    if(element.verified)
    {
        badgeImg+="verified "
        //badgeImg = '<img src='+data.badgeURL +' alt="">';
    }
    if(element.mod)
    {
        //badgeImg+="mod "
        badgeImg = '<img src="./img/mod.png"  alt="">';
        nameColor = "FFA800"
    }
    if(element.owner)
    {
        badgeImg+="owner "
        //badgeImg = '<img src='+data.badgeURL +' alt="">';
    }
    try{
    mainRow.innerHTML += "<div class='row' id="+countRows+"  style = 'background-color: rgba(0,0,0,0.5)'> <div class = 'col-sm-3' style = 'font-weight: bold; color:#"+nameColor+"'>"+badgeImg +"::" +element.user +'</div>'+ '<div class = "col-sm-9" style="color = #FFFFFF; font-weight: normal">    ' + element.message+'</div>  </div> <br>'   ; 
    }
    catch (error)
    {
        mainRow.innerHTML += "<div class = 'row' style = 'background-color: rgba(0,0,0,0.5)'>  I failed hard af </div><br>"
    }
    countRows +=1;
    if(countRows > 20)
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
   
});
    } catch (e) {
        //data = message.data
        mainRow.innerHTML += "<div class = 'row' style = 'background-color: rgba(0,0,0,0.5)'>  I failed hard af: "+e+" </div><br>"
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
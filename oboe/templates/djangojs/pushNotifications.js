function checkForMail(callback){
    $.get("/mail/newmail/", function(data){
	data = data.split(" ");
	$("{{ mailbox }}").html(data[0]);
	titledata = $("title").html().split("(")[0] + data[0]
	$("title").html(titledata);
	$.each( data.slice(1), function(index, pk){
	    $('span[newtag="' + pk + '"]').css('display','inline');
	});
    });
    if( arguments.length >= 1){
	callback.call();
    }
};

$(document).ready(function(){
    checkForMail();
    setInterval(checkForMail, 10000);
});

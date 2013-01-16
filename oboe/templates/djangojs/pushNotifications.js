function checkForMail(callback){
    $.get("/mail/newmail/", function(data){
	data = data.split(" ");
	$("{{ mailbox }}").html(data[0]);
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

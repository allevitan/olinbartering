function checkForMail(){
    $("{{ mailbox }}").load("/mail/newcount/");
};

$(document).ready(function(){
   checkForMail();
   setInterval(checkForMail, 10000);
});

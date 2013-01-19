function getScrollbarWidth() {
    var div = $('<div style="width:50px;height:50px;overflow:hidden;position:absolute;top:-200px;left:-200px;"><div style="height:100px;"></div></div>'); 
    $('body').append(div); 
    var w1 = $('div', div).innerWidth(); 
    div.css('overflow-y', 'auto'); 
    var w2 = $('div', div).innerWidth(); 
    $(div).remove(); 
    return (w1 - w2);
}

scrollwidth = getScrollbarWidth();

$(document).ready(function(){
  $(".scrollbox").css({
    "margin-right": 0 - scrollwidth,
    "padding-right": 25
  });
});

$(document).ajaxComplete(function(){
  $(".scrollbox").css({
    "margin-right": 0 - scrollwidth,
    "padding-right": 25
  });
});
function abso(){
$("{{ ident }}").css({
        height: $(window).height() - $("{{ ident }}:last").offset().top - 30
    });
}

$(window).resize(function(){
    abso();
});

$(document).ready(function(){
    abso();
});

$(document).ajaxComplete(function(){
    abso();
});
function abso(){
$("{{ ident }}").css({
        height: $(window).height() - $("{{ ident }}:last").offset().top - 50
    });
}

$(window).resize(function(){
    abso();
});

$(document).ready(function(){
    abso();
});
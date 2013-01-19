function partial(){
$("{{ ident }}").css({
    height: ($(window).height() - $("{{ ident }}:last").offset().top) {{ offset }}
    });
}

$(window).resize(function(){
    partial();
});

$(document).ready(function(){
    partial();
});

$(document).ajaxComplete(function(){
    partial();
});
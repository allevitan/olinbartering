$("{{ wantbutton }}").button();
$("{{ carpebutton }}").button();
$("{{ helpbutton }}").button();
$("{{ helpmebutton }}").button();


$("{{ wantbutton }}").click(function(){
    btn = $(this)
    if(btn.text() == 'Filter'){
	btn.button("loading")
	$("{{ wantbox }}").load("/elements/want/filtered/", function(){
	    $("{{ truncate }}").dotdotdot({watch:true});
	    btn.button('filtered');
	});
    } else {
	btn.button("loading")
	$("{{ wantbox }}").load("/elements/want/raw/", function(){
	    $("{{ truncate }}").dotdotdot({watch:true});
	    btn.button('raw');
	});
    }
});

$("{{ carpebutton }}").click(function(){
    btn = $(this)
    if(btn.text() == '+Carpe'){
	btn.button('loading');
	btn.button('with');
    } else {
	btn.button('loading');
	btn.button('without');
    }
});

$("{{ helpbutton }}").click(function(){
    btn = $(this)
    if(btn.text() == "Filter"){
	btn.button('loading');
	$("{{ helpbox }}").load("/elements/help/filtered/", function(){
	    $("{{ truncate }}").dotdotdot({watch:true});
	    btn.button('filtered');
	});
    } else {
	btn.button('loading');
	$("{{ helpbox }}").load("/elements/help/raw/", function(){
	    $("{{ truncate }}").dotdotdot({watch:true});
	    btn.button('raw');
	});
    }
});

$("{{ helpmebutton }}").click(function(){
    btn = $(this)
    if(btn.text() == '+HelpMe'){
	btn.button('loading');
	btn.button('with');
    } else {
	btn.button('loading');
	btn.button('without');
    }
});
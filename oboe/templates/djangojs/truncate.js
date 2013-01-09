$.fn.ellipsis = function()
{
    return this.each(function()
		     {
			 var el = $(this);
			 el.css("overflow", "hidden")
		             var text = el.html();
			     var t = $(this.cloneNode(true))
				 .hide()
				 .css('position', 'absolute')
				 .css('overflow', 'visible')
				 .width(el.width())
				 .height('auto')
			     ;
			     
			     el.after(t);

			     function height() { return t.height() > el.height(); };
			     
			     while (text.length > 0 && height())
			     {
				 text = text.substr(0, text.length - 1);
				 t.html(text + "...");
			     }
			     
			     el.html(t.html());
			     t.remove();
			 
		     });
};

$(document).ready(function(){
    $("{{ ident }}").ellipsis();
});
    
$(document).ready(
	function() {

		filter = $("#id_filters").val();

		if (filter == "Help?"){
			$(".price").hide();}
		else {
			$(".price").show('medium');}
	}
)

$(document).change(
	function() {

		bulletinType = $("#id_filters").val();

		if (bulletinType == "Help?"){
			$(".price").hide('medium');}
		else {
			$(".price").show('medium');}
	}
)


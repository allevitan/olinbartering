$(document).ready(
	function() {

		bulletinType = $("#id_bulletinType").val();

		if (bulletinType == "Help?"){
			$(".price").hide();}
		else {
			$(".price").show('medium');}
	}
)

$(document).change(
	function() {

		bulletinType = $("#id_bulletinType").val();

		if (bulletinType == "Help?"){
			$(".price").hide('medium');}
		else {
			$(".price").show('medium');}
	}
)


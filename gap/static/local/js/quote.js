$(function(){
	var content = $('#quote-content'),
	onSuccess = function(html){
		content.html(html);
		init();
	},
	init = function(){
		var form = $('#getquote');
		form.find('input[type=radio]').on('click',function(){
			var payload = form.serializeArray();
			$.post(document.URL, payload, onSuccess);
		});
	};
	init();	
});
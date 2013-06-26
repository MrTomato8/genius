	
$(document).ready(function () {

	// Animation for the languages and currency dropdown
	$('.switcher').hover(function() {
	$(this).find('.option').show();
	},function() {
	$(this).find('.option').hide();
	}); 
	
	/* Categories */

	$(".navigation_container nav > ul > li").hover(function () {
								
			$(this).find("div.sub-menu").eq(0).show();
								
	},function () {
		
			$(this).find("div.sub-menu").eq(0).hide();		
			
	}); 
	
		$(".navigation_container nav > ul > li > .sub-menu > ul > li ").hover(function () {
			
		  		$(this).find(".sub-menu").eq(0).show();

		},function () {
					
				$(this).find(".sub-menu").eq(0).hide();

		}); 
		
	// Cart
	$('#cart_block').hover(function() {
	$(this).find('.content').show();
	},function() {
	$(this).find('.content').hide();
	}); 
		
		
	$('.footer-navigation h3').click(function() {
		
		var element_index = $('.footer-navigation h3').index(this);
		var classe = $('.footer-navigation ul').eq(element_index).attr('class');
		
		if(classe == 'no-active') {
		
			$('.footer-navigation ul').eq(element_index).removeClass('no-active');
		
		} else {
		
			$('.footer-navigation ul').eq(element_index).addClass('no-active');
		
		}
	
	});

	$('.mobile-navigation .click-menu').click(function() {
		
		var classe = $('.categories-mobile-links > ul').attr('class');
						
		if(classe == 'active') {
		
			$('.mobile-navigation .categories-mobile-links > ul').removeClass('active');
		
		} else {
		
			$('.mobile-navigation .categories-mobile-links > ul').addClass('active');
		
		}
	
	});
	
	$('.mobile-navigation .plus').click(function() {
	
		var element_index = $('.mobile-navigation .plus').index(this);
		var classe = $('.categories-mobile-links ul ul').eq(element_index).attr('class');
		
		if(classe == 'active') {
			
			$(this).removeClass('minus');
			$('.categories-mobile-links ul ul').eq(element_index).removeClass('active');
		
		} else {
		
			$(this).addClass('minus');
			$('.categories-mobile-links ul ul').eq(element_index).addClass('active');
		
		}
	
	});

		
	/* products hover */
	
	$(".products-grid > div").hover(function () {
	
		$(this).find(".on-hover").show();
		$(this).find(".off-hover").hide();
	
	},function () {
	
		$(this).find(".on-hover").hide();
		$(this).find(".off-hover").show();

	}); 
	
	/* Ajax Cart */
	$('#cart_block .cart-heading').live('click', function() {
	
		$('#cart_block .content').show();
				
		$('#cart_block').live('mouseleave', function() {
			$('#cart_block .content').hide();
		});
	});
	
	/* autoclear function for inputs */
	$('.autoclear').click(function() {
	if (this.value == this.defaultValue) {
	this.value = '';
	}
	});

	$('.autoclear').blur(function() {
	if (this.value == '') {
	this.value = this.defaultValue;
	}
	});
	
	$(function() { $(window).scroll(function() {
			if($(this).scrollTop() > 300) {
				$('#toTop').fadeIn();	
			} else {
				$('#toTop').stop().fadeOut();
			}
		});
	 
		$('#toTop').click(function() {
			$('body,html').animate({scrollTop:0},800);
		});	
	});

	$('#q_up').click(function(){var q_val_up=parseInt($("input#quantity_wanted").val());if(isNaN(q_val_up)){q_val_up=0;}
	$("input#quantity_wanted").val(q_val_up+1).keyup(); return false; });$('#q_down').click(function(){var q_val_up=parseInt($("input#quantity_wanted").val());if(isNaN(q_val_up)){q_val_up=0;}
	if(q_val_up>1){$("input#quantity_wanted").val(q_val_up-1).keyup();;} return false; });
	
	/* Search */
	$('header .button-search').bind('click', function() {
		url = $('base').attr('href') + 'index.php?route=product/search';
				 
		var search = $('header input[name=\'search\']').attr('value');
		
		if (search) {
			url += '&search=' + encodeURIComponent(search);
		}
		
		location = url;
	});
	
	$('header .search input[name=\'search\']').bind('keydown', function(e) {
		if (e.keyCode == 13) {
			url = $('base').attr('href') + 'index.php?route=product/search';
			 
			var search = $('header .search input[name=\'search\']').attr('value');
			
			if (search) {
				url += '&search=' + encodeURIComponent(search);
			}
			
			location = url;
		}
	});
	
	$('.success img, .warning img, .attention img, .information img').live('click', function() {
		$(this).parent().fadeOut('slow', function() {
			$(this).remove();
		});
	});	
	
	$('.close').live('click', function() {
		$(this).parent().fadeOut('slow', function() {
			$(this).remove();
		});
	});	
	
});


function paginacja(id) {

	var width_module = $('#'+ id +'').width()+20;
	var width_body = $('body').width();
	var pozwolenie = true;
	var aktualny_left = 0;
			
	if(width_body > 960 && (width_module == 285 || width_module == 240)) {  
		
		var liczba_produktow = $('#'+ id +' .products-grid > div').length;
		var active = 0;
		var products = 3;
		$('#'+ id +' .products-grid > div').hide();
		$('#'+ id +' .products-grid > div').slice(0, products).show();	
		
		$('#'+ id +'_prev').click(function() {
			
			var poczatek = 0;
			
			if(active >= products) {
			
				poczatek = active-products;
			
			} else {
			
				return false;
			
			}
		
			$('#'+ id +' .products-grid > div').hide();	
			$('#'+ id +' .products-grid > div').slice(poczatek, poczatek+products).show();	
			
			if ($.browser.msie && ($.browser.version == 8 || $.browser.version == 7 || $.browser.version == 6)) {
			} else {
				 
				$('#'+ id +' .products-grid > div').slice(poczatek, poczatek+products).css("opacity", "0.3");  
				$('#'+ id +' .products-grid > div').slice(poczatek, poczatek+products).animate({opacity: 1}, 800);  

			}
			
			active = poczatek;
		
			return false;
		
		});
		
		$('#'+ id +'_next').click(function() {
			
			var koniec = 0;
			
			if(active+products < liczba_produktow) {
			
				koniec = active+products;
			
			} else {
			
				return false;
			
			}
		
			$('#'+ id +' .products-grid > div').hide();	
			$('#'+ id +' .products-grid > div').slice(koniec, koniec+products).show();	
			
			if ($.browser.msie && ($.browser.version == 8 || $.browser.version == 7 || $.browser.version == 6)) {
			} else {
				 
				$('#'+ id +' .products-grid > div').slice(koniec, koniec+products).css("opacity", "0.3");  
				$('#'+ id +' .products-grid > div').slice(koniec, koniec+products).animate({opacity: 1}, 800);  

			}
			
			active = koniec;
		
			return false;
		
		});
	
	} else {
		
		$('#'+ id +'').css("overflow", "hidden").css("width", "100%").css("position", "relative");
		$('#'+ id +' .products-grid').css("width", "9999999px");
		
		$('#'+ id +'_prev').click(function() {
		
			if(pozwolenie == true && aktualny_left > 0) {
				
				pozwolenie = false;
				
				width_module = $('#'+ id +'').width()+20;
				width_body = $('body').width();
				
				if(width_body > 960) {
					
					if(rtl == 1) {
						
			  			$('#'+ id +' .products-grid').animate({'right': '+='+width_module+'px'}, 700, function() { pozwolenie = true; } );
			  			aktualny_left = aktualny_left - width_module;
			  			
					} else {
						
			  			$('#'+ id +' .products-grid').animate({'left': '+='+width_module+'px'}, 700, function() { pozwolenie = true; } );
			  			aktualny_left = aktualny_left - width_module;
		  			
		  			}
		  		
		  		} else {
		  			
		  			if(rtl == 1) {
			  		  
			  			$('#'+ id +' .products-grid').animate({'right': '+=284px'}, 700, function() { pozwolenie = true; } );
			  			aktualny_left = aktualny_left - 284;
		  			
		  			} else {
		  			
			  			$('#'+ id +' .products-grid').animate({'left': '+=284px'}, 700, function() { pozwolenie = true; } );
			  			aktualny_left = aktualny_left - 284;
		  			
		  			}
		  		
		  		}
	  		
	  		}
	  		
	  		return false;
		
		});
		
		$('#'+ id +'_next').click(function() {
		
			if(pozwolenie == true) {
			
				pozwolenie = false;
			
				width_module = $('#'+ id +'').width()+20;
				width_body = $('body').width();
				
				if(width_body > 960) {
					
					var all_width = 0;
					$('#'+ id +' .products-grid > div').each(function(index){
						
						all_width = all_width + $(this).width() + 62;
					
					});
					
					if(aktualny_left + width_module < all_width) {
							
						if(rtl == 1) {
									
				  	  		$('#'+ id +' .products-grid').animate({'right': '-='+width_module+'px'}, 700, function() { pozwolenie = true; } );
				  	  		aktualny_left = aktualny_left + width_module;
			  	  		
			  	  		} else {
			  	  		
				  	  		$('#'+ id +' .products-grid').animate({'left': '-='+width_module+'px'}, 700, function() { pozwolenie = true; } );
				  	  		aktualny_left = aktualny_left + width_module;
			  	  		
			  	  		}
		  	  		
		  	  		} else {
		  	  		
		  	  			pozwolenie = true;
		  	  		
		  	  		}
		  		
		  		} else {
		  		
					var all_width = 0;
					$('#'+ id +' .products-grid > div').each(function(index){
						
						all_width = all_width + $(this).width() + 62;
					
					});
					
					if(aktualny_left + 350 < all_width) {
			  			
			  			if(rtl == 1) {
			  			
				  	  		$('#'+ id +' .products-grid').animate({'right': '-=284px'}, 700, function() { pozwolenie = true; } );
				  	  		aktualny_left = aktualny_left + 284;
				  	  		
			  	  		} else {
			  	  		
				  	  		$('#'+ id +' .products-grid').animate({'left': '-=284px'}, 700, function() { pozwolenie = true; } );
				  	  		aktualny_left = aktualny_left + 284;
				  	  		
			  	  		}
		  	  		
		  	  		} else {
		  	  		
		  	  			pozwolenie = true;
		  	  		
		  	  		}
		  		
		  		}
	  		
	  		}
	  		
	  		return false;
		
		});
	
	}

}

function getURLVar(key) {
	var value = [];
	
	var query = String(document.location).split('?');
	
	if (query[1]) {
		var part = query[1].split('&');

		for (i = 0; i < part.length; i++) {
			var data = part[i].split('=');
			
			if (data[0] && data[1]) {
				value[data[0]] = data[1];
			}
		}
		
		if (value[key]) {
			return value[key];
		} else {
			return '';
		}
	}
} 

function addToCart(product_id, quantity) {
	quantity = typeof(quantity) != 'undefined' ? quantity : 1;

	$.ajax({
		url: 'index.php?route=checkout/cart/add',
		type: 'post',
		data: 'product_id=' + product_id + '&quantity=' + quantity,
		dataType: 'json',
		success: function(json) {
			$('.success, .warning, .attention, .information, .error').remove();
			
			if (json['redirect']) {
				location = json['redirect'];
			}
			
			if (json['success']) {
				$('#notification').html('<div class="notification"><div class="close"></div>' + json['success'] + '</div>');
				
				$('.notification').fadeIn('slow');
				
				$('#cart_block').load('index.php?route=module/cart #cart_block > *');
				
				
			}	
		}
	});
}
function addToWishList(product_id) {
	$.ajax({
		url: 'index.php?route=account/wishlist/add',
		type: 'post',
		data: 'product_id=' + product_id,
		dataType: 'json',
		success: function(json) {
			$('.success, .warning, .attention, .information').remove();
						
			if (json['success']) {
				$('#notification').html('<div class="notification"><div class="close"></div>' + json['success'] + '</div>');
				
				$('.notification').fadeIn('slow');
				
				$('#wishlist-total').html(json['total']);
				
			}	
		}
	});
}

function addToCompare(product_id) { 
	$.ajax({
		url: 'index.php?route=product/compare/add',
		type: 'post',
		data: 'product_id=' + product_id,
		dataType: 'json',
		success: function(json) {
			$('.success, .warning, .attention, .information').remove();
						
			if (json['success']) {
				$('#notification').html('<div class="notification"><div class="close"></div>' + json['success'] + '</div>');
				
				$('.notification').fadeIn('slow');
				
				$('#compare-total').html(json['total']);
				
			}	
		}
	});
}

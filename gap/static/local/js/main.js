$(document).ready(function(){

    screen_responsive();

    $('[data-toggle="popover"]').mouseenter(function(){

        $(this).popover('show');

    }).mouseleave(function(){

        $(this).popover('hide');

    });


    $('.navbar-toggle').click(function(){

        $('#top-nav .navbar-responsive-collapse .dropdown-toggle.active, #top-nav .navbar-responsive-collapse dropdown-submenu > a').removeClass('active');

    });

    $('.dropdown-submenu a').click(function(){

        $(this).parent().find('.dropdown-menu').slideToggle();

        return false;

    });
    $('#top-nav .dropdown-toggle, #top-nav .dropdown-submenu > a').click(function(){

        $(this).toggleClass('active');

    });


});

$(window).on('resize', function(){

    screen_responsive();
    
});

function screen_responsive(){

    var screen_width = $(window).width();

    if(screen_width <= 480){

        if($('#sidebar-left-responsive').length){

            $('#sidebar-left-responsive').append($('.sidebar-left'));
            
        }

    }else{
        
        if($('#sidebar-left-responsive').length){

            $('#columns').prepend($('.sidebar-left'));
                
        }
        
    }

    if(screen_width <= 768){

        if($('#sidebar-right-responsive').length){
            
            $('#sidebar-right-responsive').append($('.sidebar-right'));
            
        }

    }else{


        if($('#sidebar-right-responsive').length){

            $('#columns').append($('.sidebar-right'));
                
        }

    }
    
}

/*FlexSlider Script
----------------------------- */
function flex_slider() {
    jQuery(window).load(function() {
        jQuery('.flexslider').flexslider({
            animation: "fade",
            startAt: 0,
            slideshow: true,
            slideshowSpeed: 7000,
            start: function(slider) {
                jQuery('body').removeClass('loading');
            }
        });
    });
}
flex_slider();

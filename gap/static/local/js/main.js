$(document).ready(function(){

    screen_responsive();

    $('[data-toggle="popover"]').mouseenter(function(){

        $(this).popover('show');

    }).mouseleave(function(){

        $(this).popover('hide');

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

    if(screen_width <= 700){

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

PPS.quoteContent = {
    init: function() {
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
    }
};

PPS.getQuote = {
    currency : '£',

    trySubmitForm: function() {
        var $form = $('#getquote'),
            customSizeConversionRatio = parseFloat($form.find('input[name=custom_size_unit]:checked').val()),
            width = parseFloat($form.find('input[name=width]').val()) * customSizeConversionRatio,
            height = parseFloat($form.find('input[name=height]').val()) * customSizeConversionRatio,
            quantity = parseFloat($form.find('input[type=text][name=quantity]').val() || $form.find('input[type=radio][name=quantity]:checked').val()),
            isCustomSizeFormValid = $form.find('input[name=width]').length ==0 || width != 0 && height != 0 && !isNaN(width) && !isNaN(height),
            isQuantityFormValid = quantity != 0 && !isNaN(quantity);
        if (isCustomSizeFormValid && isQuantityFormValid) {
            $.ajax({
                    method: 'post',
                    url: $form.attr('action'),
                    data:{
                        'width': width,
                        'height': height,
                        'quantity': quantity,
                        'csrfmiddlewaretoken': $form.find('input[name="csrfmiddlewaretoken"]').val()
                    },
                    success:function(data){
                        console.log(data);
                        PPS.getQuote.add(data.price,data.quantity)}

                })
        }
    },

    add : function(price, quantity){
        var price = parseFloat(price).toFixed(2),
        unit_price = parseFloat(price/quantity).toFixed(2);
        if (quantity > 1) {
            $('#calculated_unit_price').html('(Unit price is ' + this.currency + unit_price + ')').show();
        } else {
            $('#calculated_unit_price').html('').hide();
        }
        $('#calculated_price').html(this.currency + price);
        $('input#add_quantity').val(quantity)
        $('html, body').animate({
            scrollTop: $('.price-table').offset().top
            }, 500);
    },
    init: function(){
        var $form = $('#getquote');
        $("#quantity_picker li").on('click', function() {
            $(this).addClass('active')
                .find('input').prop('checked', true).end()
                .siblings('li').removeClass('active');
            $form.find('input[type=text][name=quantity]').val('');
            PPS.getQuote.trySubmitForm();
        });
        $form.find('input[type=text]').on('keyup', function() {
            $form.find('input[type=radio][name=quantity]').prop('checked', false).parent('li').removeClass('active');
            PPS.getQuote.trySubmitForm();
        });
        $form.find('input[name=custom_size_unit]').on('change', function() {
            $selected = $form.find('input[name=custom_size_unit]:checked');
            $form.find('.js-pickoptions-customsize-units').html($selected.data('abbreviation'));
            PPS.getQuote.trySubmitForm();
        })
    }
};

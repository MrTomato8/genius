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
    txt : function(){
        var _this=this,
        inputs=$( "#getquote input[type='text']" );
        inputs.keyup(function() {
            var frm=$(this).parents('form'),
            i=0;
            while(i<inputs.length){
                if($(inputs[i]).val()==false){return null}
                i++;
                }
            var val=frm.serialize(),
            url = frm.find('#id_quantity').data('action');
            val = val + '&'+$('input[name="csrfmiddlewaretoken"]').serialize()
            $.ajax({
                    method:'post',
                    url:url,
                    data:val,
                    success:function(data){
                        console.log(data)
                        _this.add(data.price,data.quantity)}

                })
        });
        return this
    },
    rdio: function(){
        var _this =this;
        $('#quantity_picker li, #quantity_picker span').click(function(){
            var data = $(this).data()
            _this.add(data['price'],data['quantity'])
        });
        return this
    },
    init:function(){
        this.txt()
        this.rdio()
    }
};

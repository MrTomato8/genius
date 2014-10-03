PPS.accounts = {
    init: function() {
        $('.quote-product-toggle').on('click', function(e) {
            var id = $(this).parent().parent().attr('id').replace('_row', '');
            $('#' + id + '_header').toggleClass('hidden');
            $('.' + id + '_product').toggleClass('hidden');
        	$(this).toggleClass('quote-product-toggle-up');
        });

        $('.quote-product-delete').click(function(e) {
            if (!confirm('Remove quote?'))
                return false;
        });

        $('.quote-product-email').on('click', function(e) {
            e.preventDefault();

            $.ajax({
                url: '/options/quote/send/',
                dataType : 'json',
                data: {'quote_id': $(this).attr('data-id')}
            })
            .done(function(response){
                alert(response.message);
            })
            .fail(function(response){
                $('#modal-login').modal('toggle');
            });
        });
    }
};

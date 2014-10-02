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
    }
};

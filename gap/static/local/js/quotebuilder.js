PPS.quotebuilder = {
    init: function() {
        $('.js-quotebuilder-remove-form').on('submit', function(e) {
            return confirm('Remove product?');
        });

        $('#save_quote').on('click', function(e) {
            e.preventDefault();

            $.ajax({
                url: '/options/quote/save/',
                success: function (response) {
                    $('#quote-builder > div.panel-body').html('');
                    alert(response.message);
                }
            });
        });

        $('#send_quote').on('click', function(e) {
            e.preventDefault();

            $.ajax({
                url: '/options/quote/send/',
                success: function (response) {
                    $('#quote-builder > div.panel-body').html('');
                    alert(response.message);
                }
            });
        });
    }
};

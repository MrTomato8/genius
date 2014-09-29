PPS.quotebuilder = {
    init: function() {
        $('.js-quotebuilder-remove-form').on('submit', function(e) {
            return confirm('Remove product?');
        });

        $('#print_quote').on('click', function(e) {
            if ($('input[name=can_download]').val() != '1') // show modal login popup if not authorized
            {
                $('#modal-login').modal('toggle');
                e.preventDefault();
            }
        });

        $('#save_quote').on('click', function(e) {
            e.preventDefault();

            $.ajax({
                url: '/options/quote/save/',
                dataType : 'json',
            })
            .done(function(response){
                alert(response.message);
            })
            .fail(function(response){
                $('#modal-login').modal('toggle');
            });
        });

        $('#send_quote').on('click', function(e) {
            e.preventDefault();

            $.ajax({
                url: '/options/quote/send/',
                dataType : 'json',
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

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

        $('#bespoke_quote').on('click', function(e) {
            e.preventDefault();
            $('#modal-bespoke').modal('toggle');
        });

        $("#bespoke_form").validate({
            rules: {
                'quote-name': "required",
                'quote-email': {
                    required: true,
                    email: true
                },
                'quote-phone': "required",
                'quote-text': "required",
            },
            messages: {
                'quote-name': "Please enter your name",
                'quote-email': "Please enter a valid email address",
                'quote-phone': "Please enter your phone",
                'quote-text': "Please enter text"
            },
            submitHandler: function(form) {
                form = $(form);
                $.ajax({
                    url: form.attr("action"),
                    type: 'POST',
                    data: form.serialize(),
                    dataType : 'json',
                })
                .always(function(response){
                    $('#modal-bespoke').modal('toggle');
                    alert(response.message);
                });

                return false;
            }
        });
    }
};

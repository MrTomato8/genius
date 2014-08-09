PPS.pickForm = {
    init: function() {
        var calculared = false;

        $('.panel-default.last .option-choice .radio-choice').click(function () {
            $.ajax({
                data: $('form#pickoptions').serialize(),
                type: $('form#pickoptions').attr('method'),
                url: $('form#pickoptions').attr('action'),
                success: function (response) {
                    x = $('<div></div>');
                    x.html(response);
                    res = x.find('#getquote_wrap');
                    if (!res.html()) {
                        res = x.find('#form-errors');
                        $('#form-errors').html(res);
                        $('#modalchangepw').html('');
                    }
                    else {
                        $('#modalchangepw').html(res);
                        $('#form-errors').html('');
                    }
                }
            });
            calculared = true;
            return false;
        });

        $('.option-choice .radio-choice').click(function () {
            if (calculared) {
                var quantity = $('#quantity_picker input:checked').attr('value');
                $.ajax({
                    data: $('form#pickoptions').serialize(),
                    type: $('form#pickoptions').attr('method'),
                    url: $('form#pickoptions').attr('action'),
                    success: function (response) {
                        x = $('<div></div>');
                        x.html(response);
                        res = x.find('#getquote_wrap');
                        if (!res.html()) {
                            res = x.find('#form-errors');
                            $('#form-errors').html(res);
                            $('#modalchangepw').html('');
                        }
                        else {
                            $('#modalchangepw').html(res);
                            $('#form-errors').html('');
                        }
                        $('li[data-qty="' + quantity + '"]').trigger("click");
                    }
                });
            }
            prev = $(this).first().closest('.panel-collapse');
            prev.collapse('toggle').siblings('a.panel-heading').addClass('collapsed');
            next = prev.parent('.panel').next();
            if (next.hasClass('group_name')) next = next.next().children('.panel-collapse');
            else next = next.children('.panel-collapse');
            next.collapse('show').siblings('a.panel-heading').removeClass('collapsed');
            PPS.pickForm.refreshSelectedChoicesList()
        });

        $(".radio-choice").click(disableConflictingChoices);

        $('input.radio-choice').attr("checked", false);
    },

    refreshSelectedChoicesList: function() {
        $('#selected-choices ul').html('');
        $('.option-choice .radio-choice:checked').each(function (a, b) {
            $('#selected-choices ul').append('<li>' + $(b).closest('li').html() + '</li>')
        });
        if (PPS.multifileForm.isMultifileEnabled()) {
            $('#selected-choices ul').append('<li>multifile<br><img src="' + STATIC_URL + 'options/img/multifile.png" alt="none"><br></li>')
        }
    }
};

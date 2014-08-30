PPS.pickForm = {
    init: function() {
        $('#pickoptions .panel-default .radio-choice').click(function () {
            if ($('#pickoptions .panel-default:not(:has(.radio-choice:checked))').length) {
                // Not all options selected
                return;
            }
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
                    $('#id_quantity').trigger("keyup");
                }
            });
        });

        $('#pickoptions .radio-choice').click(function () {
            prev = $(this).first().closest('.panel-collapse');
            prev.collapse('toggle').siblings('a.panel-heading').addClass('collapsed');
            next = prev.parent('.panel').next();
            if (next.hasClass('group_name')) next = next.next().children('.panel-collapse');
            else next = next.children('.panel-collapse');
            next.collapse('show').siblings('a.panel-heading').removeClass('collapsed');
            PPS.pickForm.refreshSelectedChoicesList()
        });

        $("#pickoptions .radio-choice").click(disableConflictingChoices);
        this.refreshSelectedChoicesList();
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

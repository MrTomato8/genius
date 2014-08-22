PPS.quotebuilder = {
    init: function() {
        $('.js-quotebuilder-remove-form').on('submit', function(e) {
            return confirm('Remove product?');
        });
    }
};
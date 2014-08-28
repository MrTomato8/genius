PPS.basket = {
    init: function() {
        $('#basket_formset .js-toggle-item-on').click(function(e) {
            e.preventDefault();
            PPS.basket.POSTtoLink(this);
        });
        $('#basket_formset .js-remove-item').click(function(e) {
            e.preventDefault();
            if (confirm('Remove product?')) {
                PPS.basket.POSTtoLink(this);
            }
        });
    },

    /**
     * Send POST request to where <a> tag links
     * @param link_tag HTMLAnchorElement
     */
    POSTtoLink: function(link_tag) {
        $('<form action="' + link_tag.href + '" method="POST">' +
            '<input type="hidden" name="csrfmiddlewaretoken" value="' + $('input[name=csrfmiddlewaretoken]').val() + '">' +
          '</form>').submit();

    }
};

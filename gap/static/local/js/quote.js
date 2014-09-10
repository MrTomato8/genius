PPS.getQuote = {
    currency : '£',
    $priceLabel: $('#calculated_price'),
    $unitPriceLabel: $('#calculated_unit_price'),
    $sizeFormErrorLabel: $('#size_form_error'),

    trySubmitForm: function() {
        var $form = $('#getquote'),
            customSizeConversionRatio = parseFloat($form.find('input[name=custom_size_unit]:checked').val()),
            width = parseFloat($form.find('input[name=width]').val()) * customSizeConversionRatio,
            height = parseFloat($form.find('input[name=height]').val()) * customSizeConversionRatio,
            quantity = PPS.multifileForm.calculateTotalQuantity(),
            isCustomSizeFormValid = $form.find('input[name=width]').length ==0 || width != 0 && height != 0 && !isNaN(width) && !isNaN(height),
            isQuantityFormValid = quantity && !isNaN(quantity);
        this.clearAjaxFields();
        if (isCustomSizeFormValid && isQuantityFormValid) {
            $.ajax({
                    method: $form.attr('method'),
                    url: $form.attr('action'),
                    data:{
                        'width': width,
                        'height': height,
                        'quantity': quantity,
                        'number_of_files': PPS.multifileForm.$files.val(),
                    },
                    success:function(data){
                        if (data.valid) {
                            PPS.getQuote.add(data.total_price, data.unit_price,data.quantity, data.get, data.action)
                        } else {
                            PPS.getQuote.handleAjaxError(data);
                        }
                    }
                });
        }
    },

    clearAjaxFields: function() {
        this.$priceLabel.html('');
        this.$unitPriceLabel.html('').hide();
        this.$sizeFormErrorLabel.html('');
    },

    add : function(total_price, unit_price, quantity,get,action){
        var price = parseFloat(total_price).toFixed(2),
        unit_price = parseFloat(unit_price).toFixed(2),
        form = $('#calculated_price').parent().find('form');
        form.attr('action',action);
        console.log(action)
        console.log(form)
        form.attr('action',action);
        if (quantity > 1) {
            $('#calculated_unit_price').html('(Unit price is ' + this.currency + unit_price + ')').show();
        }
        $('#calculated_price').html(this.currency + price);
        $('html, body').animate({
            scrollTop: $('.price-table').offset().top
        }, 500);
    },

    handleAjaxError: function(data) {
        if (data.size_form_error) {
            this.$sizeFormErrorLabel.html(data.size_form_error).show();
        }
    },

    toggleQuantityRadio: function($radio, isOn) {
        $radio.prop('checked', isOn).parent('li').toggleClass('active', isOn);
    },

    init: function(){
        PPS.multifileForm.init();

        this.$priceLabel =$('#calculated_price');
        this.$unitPriceLabel =$('#calculated_unit_price');
        this.$sizeFormErrorLabel = $('#size_form_error');

        var $form = $('#getquote');
        $("#quantity_picker li").on('click', function() {
            $(this).siblings('li').removeClass('active');
            $form.find('input[name=quantity]').val($(this).data('quantity')).trigger('change');
            PPS.getQuote.trySubmitForm();
        });
        $form.find('input[name=quantity]').on('keyup', function() {
            var value = parseInt($(this).val());
            PPS.getQuote.toggleQuantityRadio($form.find('input[name=quantity_radio]'), false);
            PPS.getQuote.toggleQuantityRadio($form.find('input[name=quantity_radio][value=' + value + ']'), true);
            PPS.getQuote.trySubmitForm();
        });
        $form.find('input[name=custom_size_unit]').on('change', function() {
            $selected = $form.find('input[name=custom_size_unit]:checked');
            $form.find('.js-pickoptions-customsize-units').html($selected.data('abbreviation'));
            $form.find('input[name=width],input[name=height]').val('');
            PPS.getQuote.trySubmitForm();
        })
    }
};

PPS.multifileForm = {
    $files: $(),
    $total_quantity: $(),
    $toggle: $(),

    init: function() {
        this.$files = $('input[name=number_of_files]');
        this.$total_quantity = $('input[name=total_quantity]');
        this.$toggle = $('#multifile_toggle');

        this.$toggle.on('click', $.proxy(this.toggleMultifileInputs, this));

        $('#multifile_files_up_button').on('click', $.proxy(this.changeFilesBy, this, +1));
        $('#multifile_files_down_button').on('click', $.proxy(this.changeFilesBy, this, -1));

        this.$files.add($('input[name=quantity]')).on('keyup change', $.proxy(this.updateTotalQuantity, this));
    },

    toggleMultifileInputs: function() {
        this.$toggle.toggleClass('active');
        $('#multifile_inputs').slideToggle();
        $('#choose_quantity_label').html(this.$toggle.hasClass('active') ? 'Choose or enter quantity for each' : 'Choose or enter quantity');
        PPS.pickForm.refreshSelectedChoicesList();
        PPS.getQuote.trySubmitForm();
    },

    changeFilesBy: function(delta) {
        var current = parseFloat(this.$files.val()) || 0;
        this.$files.val(Math.max(1, current + delta));
        this.$files.trigger('change');
        return false;
    },

    calculateTotalQuantity: function() {
        var quantity = parseInt($('input[name=quantity]').val()),
            files = parseInt(this.$files.val());
        if (this.isMultifileEnabled()) {
            if (quantity && files && !isNaN(quantity) && !isNaN(files)) {
                return Math.max(0, quantity * files);
            }
        } else {
            return quantity;
        }
        return NaN;
    },

    updateTotalQuantity: function() {
        var quantity = this.calculateTotalQuantity();
        this.$total_quantity.val(quantity && !isNaN(quantity) ? quantity : '');
        PPS.getQuote.trySubmitForm();
    },

    isMultifileEnabled: function() {
        return this.$toggle.is('.active');
    }
};

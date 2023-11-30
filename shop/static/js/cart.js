
var updateBtns = document.getElementsByClassName('add_to_cart_btn')
for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {

        var _productId = this.dataset.id
        var _productTitle = this.dataset.name
        var _productImage = this.dataset.image
        var _qty = this.dataset.qty
        var _productPrice = this.dataset.price
        var _action = this.dataset.action
        console.log("_action:", _action, "product_id: ", _productId, "product_name: ", _productTitle, "product_qty: ", _qty, "product_price: ", _productPrice)

        var _vm = $(this);
        // Ajax
        $.ajax({
            url: '/eshop/cart/',
            data: {
                'id': _productId,
                'image': _productImage,
                'qty': _qty,
                'action': _action,
                'price': _productPrice,
                'title': _productTitle,
            },
            dataType: 'json',
            beforeSend: function () {
                _vm.attr('disabled', true);
            },
            success: function (res) {
                $(".cart-list").text(res.totalitems);
                _vm.attr('disabled', false);
            }
        });

        // End
    });
    // End

}


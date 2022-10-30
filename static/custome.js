$(document).ready(function () {
    $('#loadmore').on('click',function () {
            var _curentProducts = $('.product-box').length;
            var _limit=$(this).attr('data-limit');
            var _total=$(this).attr('data-total');
            console.log(_curentProducts,_limit,_total)
    //    start ajax
            $.ajax({
                url : '/loadmode_data',
                data : {
                    'limit':_limit,
                    'offset':_curentProducts,
                    'total':_total
                },
                dataType : 'json',
                beforeSend : function () {
                    $('#loadmore').attr('disabled',true);
                    $('.load-more-icon').addClass('fa-spin');
                },
                success : function (res) {
                    console.log(res.data)
                    $('#filteredproducts').append(res.data);
                    $('#loadmore').attr('disabled',false);
                    $(".load-more-icon").removeClass('fa-spin');
                    // remove the loadmore button
                    var _totalshowing = $('.product-box').length;
                    if ( _totalshowing==_total){
                        $('#loadmore').remove()
                    }
                }
            });
    // end ajax
    });

    // product variation price based on color and wuantity
    $('.choose-size').hide();
    //    end


//    show sizes according selecting colors
    $('.choose-color').on('click',function () {
        $('.choose-size').removeClass('active');
        $('.choose-color').removeClass('focused');
        $(this).addClass('focused');

        var _color = $(this).attr('data-color');
        // console.log(_color)
        $('.choose-size').hide();
        $('.color'+_color).show();
        $('.color'+_color).first().addClass('active')
        var _price = $('.color'+_color).first().attr('data-price');
          $('.product-price').text(_price)
    });
//    end


// show the first selected color first selected size
    $(".choose-color").first().addClass('focused');
    var _color = $('.choose-color').first().attr('data-color');
    var _price = $('.choose-size').first().attr('data-price');
    $('.color'+_color).show();
    $('.color'+_color).first().addClass('active');
    // $(".product-price").text(_price);

    //    end

//    show the price according the selected size
    $('.choose-size').on('click',function () {
        var _price = $(this).attr('data-price');
        $('.choose-size').removeClass('active');
        $(this).addClass('active')
        console.log(_price)
        $('.product-price').text(_price)
    });
//    end

//    add to cart functionality
        $(document).on('click','.addToCart',function () {
            var _vm=$(this);
            var _index = _vm.attr('data-index')
            console.log(_index)
            var _qty =$('.product-qty-'+_index).val()
            var _productid = $('.product-id-'+_index).val();
            var _producttitle = $('.product-title-'+_index).val();
            var _productprice = $('.product-price-'+_index).text();
            var _productimage = $('.product-image-'+_index).val();
            // console.log(_productimage)
            console.log(_qty,_productid,_producttitle,_productprice,_productimage)
        //    ajax
            $.ajax({
                url : '/add_to_cart',
                data : {
                    'id':_productid,
                    'qty': _qty,
                    'title':_producttitle,
                    'price':_productprice,
                    'image':_productimage
                },
                dataType: 'json',
                beforeSend:function () {
                    _vm.attr('disabled',true)
                },
                success:function (res) {
                    console.log(res.data);
                    $('.cart-list').text(res.totalitems);
                    _vm.attr('disabled',false);

                }
            });
        //    end ajax


        });
//    end add to cart functionality
    //    delete cart item
        $(document).on('click','.delete-item',function () {
                var _pid = $(this).attr('data-item');
                var _vm = $(this);
                console.log(_pid);
            //    ajax code
                $.ajax({
                    url : '/delete_from_cart',
                    data:{
                        'id':_pid
                    },
                    contentType:'json',
                    beforeSend:function () {
                        _vm.attr('disabled',true);
                    },
                    success:function (res) {
                        console.log(res );
                        _vm.attr('disabled',false);
                        $('.cart-list').text(res.totalitems);
                        $('#cartlist').html(res.data)

                    }
                });
            //    ajax end
            });
        //    end for delete cart item

//    update cart item in cart list page
    $(document).on('click','.update-data',function () {
            var p_id = $(this).attr('data-item');
            var p_qty = $('.product-qty-'+p_id).val();
            var _vm=$(this);
            console.log(p_id,p_qty)
    //    ajax start
            $.ajax({
                url : '/update_cart_item',
                data:{
                    'id':p_id,
                    'qty':p_qty
                },
                contentType: 'json',
                beforeSend:function () {
                    _vm.attr('disabled',true)
                },
                success:function (res) {
                    console.log(res.data);
                    _vm.attr('disabled',false);
                    $('#cartlist').html(res.data)

                }
            });
    //    ajax end
    });
//    end update item in cart list page

//    save product review
    $('#addform').submit(function (e) {
        $.ajax({
            data:$(this).serialize(),
            method:$(this).attr('method'),
            url:$(this).attr('action'),
            dataType:'json',
            success:function (res) {
                if (res.bool==true){
                    $('.ajax-response').html('data has been added....');
                    console.log(res)
                    $('#reset').trigger('click');
                    $('.reviewBtn').hide();
                    // create data for review
                    var _html='<blockquote class="blockquote text-right">';
                    _html +='<small>+res.data.review_text+</small>';
                    _html +='<footer class="blockquote-footer">'+res.data.user;
                    _html +='<cite title="Source Title">';
                    for (var i=1; i<=res.data.review_rating; i++){
                        _html +='<i class="fa fa-star text-warning"></i>'
                    }
                    _html +='</cite>';
                    _html +=' </footer>';
                    _html +='</blockquote>'
                    _html +='<hr />'
                    $('.no-data').hide();
                    // prepend for data to review
                    $('.review-list').prepend(_html);
                //    hide the review popup box
                    $('#productreview').hide();
                    $('.avg_rating').text(res.avg_rating.avg_rating.toFixed(1));
                }
            }
        });
        e.preventDefault();
    });
//    end product review
// add wish list items for user
    $(document).on('click','.add_wish_list',function () {
        var _pid=$(this).attr('add-product');
        var _vm=$(this);
        console.log(_pid);
    //    ajax start
        $.ajax({
            url:'/add_whish_list',
            data:{
                'p_id':_pid
            },
            dataType:'json',
            success:function (res){
                console.log(res);
               if(res.bool==true){
                    _vm.addClass('disabled').removeClass('add_wish_list');
               };
        }
        })
    //    ajax end
    })
//    end wish list
});
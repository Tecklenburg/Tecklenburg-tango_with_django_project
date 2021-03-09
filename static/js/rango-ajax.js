$(document).ready(function(){


   $('#TEST').click(function() {
       alert()
       $("button").click(function(){alert('remove p')});
       $("p").remove();
   });


    $('#like_btn').click(function(){
        var categoryIdVar;
        categoryIdVar = $(this).attr('data-categoryid');

        $.get('/rango/like_category/',
            {'category_id': categoryIdVar},
            function(data){
                $('#like_count').html(data);
                $('#like_btn').hide();
            })
    });

    $('#search-input').keyup(function(){
        var query;
        query = $(this).val();

        $.get('/rango/suggest/',
            {'suggestion': query},
            function(data){
                $('#categories-listing').html(data);
            })
    });

    $('.rango-page-add').click(function(){
        var categoryid = $(this).attr('data-categoryid');
        var title = $(this).attr('data-title');
        var url = $(this).attr('data-url');
        var clickedButton = $(this);

        $.get('/rango/search_add_page/',
            {'category_id': categoryid, 'title': title, 'url': url},
            function (data){
                $('#page-listing').html(data);
                clickedButton.hide();
            })
    });

    $('.rango-add-user').click(function(){
        var clickedButton = $(this);
        var username = $(this).attr('data-username');
        var user_id = $(this).attr('data-user-id');
        document.getElementById('current-members-names').append(", " + username);
        var curr_ids = document.getElementById('current-members-ids').getAttribute('value');
        var new_ids = curr_ids + ',' + user_id;
        document.getElementById('current-members-ids').setAttribute('value', new_ids);
        clickedButton.hide();
    });

    $('.rango-open-chat').click(function(){
        var chat_id = $(this).attr('data-chat-id');
        var user_id = $(this).attr('data-user-id');
        $.ajax('/rango/')
    });


});
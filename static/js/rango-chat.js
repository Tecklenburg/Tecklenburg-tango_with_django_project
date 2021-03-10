$(document).ready(function() {
    var textarea = document.getElementById('chat-window');
    textarea.scrollTop = textarea.scrollHeight;
    var latest_message_id = -1;

    $('#chat-message-input').focus();
    document.querySelector('#chat-message-input').onkeyup = function (e) {
        if (e.keyCode === 13) {  // enter, return
            document.querySelector('#chat-message-submit').click();
        }
    };

    document.querySelector('#chat-message-submit').onclick = function () {
        var chat_id = document.getElementById('data-chat-id').value;
        var messageInputDom = document.querySelector('#chat-message-input');
        var message = messageInputDom.value;
        var user_id = $(this).attr('data-user-id');
        document.getElementById('chat-message-input').value = '';

        if (message !== '') {
            $.get('/rango/chat_add_message/',
                {'message': message, 'user_id': user_id, 'chat_id': chat_id},
                function (data) {
                    $('#chat-log').html(data);
                    var textarea = document.getElementById('chat-window');
                    textarea.scrollTop = textarea.scrollHeight;
                })
        }
        ;
    };

    var intervalId = window.setInterval(function () {
        var chat_id = document.getElementById('data-chat-id').value;
        $.get('/rango/message_check/',
            {'latest_message_id': latest_message_id, 'chat_id': chat_id},
            function (data) {
                if (data !== 'False') {
                    $.get('/rango/chat_update/',
                        {'chat_id': chat_id},
                        function (data) {
                            $('#chat-log').html(data);
                            var textarea = document.getElementById('chat-window');
                            textarea.scrollTop = textarea.scrollHeight;
                        });
                    latest_message_id = data;
                }
            })
    }, 10000);
});
$(document).ready(function(){
    function clear_participants(){
        $('#cusr_list ul').html('');
    }
    function add_participant(u){
        var real = u.real;
        // {% verbatim %}
        var template = '<li class="chat-users-list-li">                                                 \
            <div class="chat-users-participant" data-id="{{id}}" data-name="{{first_name}} {{last_name}}" data-type="{{type}}">    \
                <div class="chat-users-participant-type">{{type}}</div>                                 \
                <div class="chat-users-participant-photo"></div>                                        \
                <div class="chat-users-participant-info">                                               \
                    <div class="chat-users-participant-name">{{first_name}} {{last_name}}</div>         \
                    <div class="chat-users-participant-email">{{email}}</div>                           \
                    <div class="chat-users-participant-patient-age">{{sex}} {{age}}</div>               \
                </div>                                                                                  \
            </div>                                                                                      \
        </li>';
        // {% endverbatim %}
        var data = {id: real.id, type: u.type, first_name: real.first_name, last_name: real.last_name, email: u.email, sex: real.sex, age: real.age};
        nunjucks.configure({ autoescape: true });
        var participant = nunjucks.renderString(template, data);
        $('#cusr_list ul').append($(participant));
    }
    var CHAT_PEERS = {};
    function create_chat_box(u){
        var exists = false;
        $('#cboxs .chat-box').each(function(){
            var id = $(this).data('target');
            if(id == u.id){
                exists = true;
            }
        })
        if(exists) return;
        // {% verbatim %}
        var template = '<div class="chat-box" data-target="{{id}}" data-last="0">                   \
                            <div class="chat-box-title">                                            \
                                <div class="chat-box-title-name">{{name}}</div>                     \
                                <div class="chat-box-title-control chat-box-title-close glyphicon glyphicon-remove"></div>   \
                                <div class="chat-box-title-control chat-box-title-hide glyphicon glyphicon-minus"></div>     \
                            </div>                                                                  \
                            <div class="chat-box-body">                                             \
                            </div>                                                                  \
                            <div class="chat-box-write">                                            \
                                <div class="chat-box-write-input"></div>                            \
                                <div class="chat-box-write-send">                                   \
                                    <div class="input-group">                                       \
                                        <input type="text" class="form-control" placeholder="message" aria-describedby="sizing-addon2"> \
                                        <span class="input-group-btn">                              \
                                            <button type="submit" class="chat-send-btn btn btn-default glyphicon glyphicon-send"></button> \
                                        </span>                                                     \
                                    </div>                                                          \
                                </div>                                                              \
                            </div>                                                                  \
                        </div>';
        // {% endverbatim %}
        var box = $(nunjucks.renderString(template, u));
        $('#cboxs').append(box);
        CHAT_PEERS[u.id] = box;
        fetch_messages(u.id, box);
        return box;
    }
    function fetch_messages(id, box){
        var last_id = parseInt(box.attr('data-last'));
        console.log(last_id);
        $.ajax({
            url: '/pulse/chat/'+id+'/'+last_id
        }).done(function(content, status, xhr){
            var content_length = content.length;
            var latest_id = xhr.getResponseHeader('Last-Id');
            if(content_length){
                console.log(content);
                var body = box.find('.chat-box-body')[0];
                var messages = $($.trim(content.replace(/\s+/g, " ")));
                $(body).append(messages);
                box.attr('data-last', latest_id);
            }
            if(id in CHAT_PEERS){
                setTimeout(function(){
                    fetch_messages(id, box);
                }, 500);
            }
        });
    }
    $('#user_search').keyup(function(){
        clear_participants();
        var value = $(this).val();
        if(value.length < 2) return;
        $.ajax({
            url: '/api/v1/usercatalog/?query='+value,
            dataType : "json",
            contentType: "application/json; charset=utf-8"
        }).done(function(content, status, xhr){
            $.each(content.objects, function(i, v){
                add_participant(v);
            });
        });
    });
    $('#cusr_list .chat-users-list-ul').on("click", ".chat-users-list-li .chat-users-participant", function(){
        var participant = {id: $(this).data("id"), name: $(this).data("name"), type: $(this).data("type")};
        var box = create_chat_box(participant);
    })
    $('#cboxs').on("click", "button.chat-send-btn", function(){
        var box = $(this).closest('.chat-box');
        var msg = $(this).parent().prev().val();
        var target = box.data('target');
        alert(1);
        $.ajax({
            method: "POST",
            url: '/chat/send/',
            dataType : "json",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({to: target, mime: 'text/plain', message: msg, ctime: (new Date())})
        }).done(function(content, status, xhr){
            console.log(content);
        });
    })
});
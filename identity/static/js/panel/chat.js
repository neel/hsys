$(document).ready(function(){
    function clear_participants(){
        $('#cusr_list ul').html('');
    }
    function add_participant(u){
        var real = u.real;
        if(real == undefined) return;
        // {% verbatim %}
        var template = '<li class="chat-users-list-li">                                                 \
            <div class="chat-users-participant" data-id="{{id}}" data-name="{{first_name}} {{last_name}}" data-type="{{type}}">    \
                <div class="chat-users-participant-type chat-user-participant-type-{{type}}">{{type}}</div>                                 \
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
        if(exists) return CHAT_PEERS[u.id];
        // {% verbatim %}
        var template = '<div class="chat-box" data-target="{{id}}">                   \
                            <div class="chat-box-title">                                            \
                                <div class="chat-box-title-name">{{name}}</div>                     \
                                <div class="chat-box-title-control chat-box-title-close glyphicon glyphicon-remove"></div>   \
                                <div class="chat-box-title-control chat-box-title-hide glyphicon glyphicon-minus"></div>     \
                            </div>                                                                  \
                            <div class="chat-box-body">                                             \
                                <ul class="chat-users-list-ul"> </ul>                               \
                            </div>                                                                  \
                            <div class="chat-box-write">                                            \
                                <div class="chat-box-write-input"></div>                            \
                                <div class="chat-box-write-send">                                   \
                                    <div class="input-group">                                       \
                                        <input type="text" class="form-control chat-send-input" placeholder="message" aria-describedby="sizing-addon2"> \
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
        return box;
    }
    function fetch_messages(){
        var last_id = parseInt($('#cboxs').attr('data-last'));
        console.log('fetching messages', last_id);
        $.ajax({
            url: '/pulse/chat/'+last_id,
            dataType: 'json',
            contentType: "application/json; charset=utf-8"
        }).done(function(content, status, xhr){
            var latest_id = xhr.getResponseHeader('Last-Id');
            console.log(content);

            for(key in content){
                value = content[key];
                var msgs = value.chunk;
                var user = value.user;

                var box = CHAT_PEERS[key];
                console.log(user, box);
                if(box == undefined){
                    box = create_chat_box(user);
                }
                
                var body = box.find('.chat-users-list-ul')[0];
                var messages = $($.trim(msgs.replace(/\s+/g, " ")));
                $(body).append(messages);
            };
            if(latest_id) $('#cboxs').attr('data-last', latest_id);
            console.log(status);
            setTimeout(function(){
                fetch_messages();
            }, 500);

    }).fail(function(xhr, status, error){
        console.log(status, error, xhr.responseText);
        setTimeout(function(){
            fetch_messages();
        }, 500);
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

        var self = this;
        var target = box.data('target');
        $.ajax({
            method: "POST",
            url: '/chat/send/',
            dataType : "json",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({to: target, mime: 'text/plain', message: msg, ctime: (new Date())})
        }).done(function(content, status, xhr){
            console.log(content);
            $(self).parent().prev().val('');
        });
    });
    $('#cboxs').on("keypress", "input.chat-send-input", function(e){
        if(e.which == 13){
            $($(this).next().find('.chat-send-btn')[0]).trigger('click');
        }
    });
    $('#cboxs').on("click", "div.chat-send-close", function(){
        
    });
    $('#cboxs').on("click", "div.chat-box-title-hide", function(){
        var box = $(this).closest('.chat-box');
        var body = $(box).find('.chat-box-body');
        var writer = $(box).find('.chat-box-write');
        var state = $(box).attr('data-state');
        if(state == undefined)
            state = 'opened'

        console.log(state, state == 'opened', body, writer);
        if(state == 'opened'){
            body.css('display', 'none');
            writer.css('display', 'none');
            box.css('margin-top', '270px');
            box.attr('data-state', 'closed');
        }else{
            box.css('margin-top', '0px');
            body.css('display', 'block');
            writer.css('display', 'block');
            box.attr('data-state', 'opened');
        }
    });
    fetch_messages();
});
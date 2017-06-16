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
    var init_video = null;
    var CHAT_PEERS = {};
    var WEBRTC_PEERS = {};
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
                            <video class="chat-box-video local chat-box-camera" autoplay />                            \
                            <video class="chat-box-video remote chat-box-screen" autoplay />                           \
                            <div class="chat-box-title">                                            \
                                <div class="chat-box-title-name">{{name}}</div>                     \
                                <div class="chat-box-title-control chat-box-title-close glyphicon glyphicon-remove"></div>   \
                                <div class="chat-box-title-control chat-box-title-hide glyphicon glyphicon-minus"></div>     \
                                <div class="chat-box-title-control chat-box-title-call glyphicon glyphicon-modal-window"></div>   \
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
                var target = key;
                
                var body = box.find('.chat-users-list-ul')[0];
                var messages = $($.trim(msgs.replace(/\s+/g, " ")));
                $(body).append(messages);

                var meta = messages.find('.chat-data-meta');
                if(meta.length > 0){
                    console.log("abol");
                    $(meta).each(function(){
                        console.log("tabol");
                        var data   = this;
                        var type   = $(this).attr('data-type');
                        var value  = $(this).val();
                        console.log("TYPE "+type);
                        if(type == 'init'){
                            // initialize video conversation
                            console.log("INITIALIZING LOCAL VIDEO");
                            init_video(box);
                        }else if(type == 'sdp'){
                            console.log("SDP RECIEVED");
                            var signal = JSON.parse(value);
                            if(WEBRTC_PEERS[target]){
                                connection = WEBRTC_PEERS[target];
                                connection.setRemoteDescription(new RTCSessionDescription(signal.sdp), function(){
                                    if(signal.sdp.type == 'offer'){
                                        connection.createAnswer(function(description){
                                            got_description(target, description);
                                        }, function(error){
                                            console.log(error);
                                        });
                                    }
                                });
                            }
                        }else if(type == 'ice'){
                            console.log("ICE RECIEVED");
                            var signal = JSON.parse(value);
                            if(WEBRTC_PEERS[target]){
                                connection = WEBRTC_PEERS[target];
                                connection.addIceCandidate(new RTCIceCandidate(signal.ice));
                            }
                        }
                        console.log(data);
                    })
                }
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
    send_message = function(target, mime_type, msg, callback){
        $.ajax({
            method: "POST",
            url: '/chat/send/',
            dataType : "json",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({to: target, mime: mime_type, message: msg, ctime: (new Date())})
        }).done(function(content, status, xhr){
            callback(content, status, xhr);
        });
    }
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

    var got_description = function(target, description){
        connection.setLocalDescription(description, function(){
            send_message(target, 'chat/sdp', JSON.stringify({'sdp': description}), function(){
                // show call initiated (sdp)
                console.log("SENDING SDP");
            });
        }, function(error){
            console.log(error);
        })
    }

    var init_video = function(box, is_caller){
        var local_video = box.find('video.local');
        var target = box.data('target');

        navigator.getMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;
        navigator.getMedia({video: true}, function(stream){
            var video = local_video[0];
            video.src = (window.URL || window.webkitURL).createObjectURL(stream);

            if(is_caller){
                send_message(target, 'chat/init', '.', function(){
                    console.log("SENDING INIT");
                    // show call in progress (ice)
                });
            }

            var config = {'iceServers': [{'url': 'stun:stun.services.mozilla.com'}, {'url': 'stun:stun.l.google.com:19302'}]};
            connection = new RTCPeerConnection(config);
            connection.onicecandidate = function(event){
                if(event.candidate != null){
                    send_message(target, 'chat/ice', JSON.stringify({'ice': event.candidate}), function(){
                        console.log("SENDING ICE");
                        // show call in progress (ice)
                    });
                }
            };
            connection.onaddstream = function(event){
                var remote_video = box.find('video.remote');

                console.log('got remote stream', event);
                var remote_video = remote_video[0];
                remote_video.src = window.URL.createObjectURL(event.stream);
            };
            if(stream) connection.addStream(stream);
            if(is_caller){
                setTimeout(function(){
                    connection.createOffer(function(description){
                        got_description(target, description)
                    }, function(error){
                        console.log(error);
                    });
                }, 5000);
            }
            console.log(WEBRTC_PEERS[target], !WEBRTC_PEERS[target]);
            if(!WEBRTC_PEERS[target]){
                console.log("SETTING LOCAL CONNECTION");
                WEBRTC_PEERS[target] = connection;
                box.find('.chat-box-video').show();
            }
        }, function(error){
            console.log(error);
        });
    }

    $('#cboxs').on("click", "div.chat-box-title-call", function(){
        var button = $(this);
        var box = $(this).closest('.chat-box');
        init_video(box, true);
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
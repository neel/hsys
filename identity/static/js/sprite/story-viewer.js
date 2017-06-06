$(document).ready(function(){
    $(document).on('click', "div.story-viewer-close", function(event){
        $(this).parent().hide();
    });
    $(document).on('click', "div.story-viewer .ministory-linked", function(event){
        var refered_id = $($(this).find('.ministory-sprite')[0]).data('id');
        // $('.story-viewer').remove();
        var id = refered_id;
        $.ajax({
            url: '/_story/'+id
        }).done(function(content, status, xhr){
            var content_length = content.length;
            if(content_length){
                var story_board = $($.trim(content.replace(/\s+/g, " ")));
                $('#main').append(story_board);
                story_board.css('left', story_board.outerWidth()*($('.story-viewer').length-1));
            }
        });
    })
});
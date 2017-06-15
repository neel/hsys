$(document).ready(function(){
    $(document).on('click', "div.story-viewer-close", function(event){
        $(this).parent().hide();
        $(this).parent().remove();
    });
    $(document).on('click', "div.story-viewer .ministory-linked", function(event){
        var refered_id = $($(this).find('.ministory-sprite')[0]).data('id');
        // $('.story-viewer').remove();
        var story_already_open = false;
        $('.story-viewer').each(function(){
            var story_id = $(this).data('story');
            if(story_id == refered_id){
                story_already_open = true;
                var prestate = $(this).css('border');
                $(this).css('border', '2px solid yellow');
                var self = $(this);
                setTimeout(function(){
                    self.css('border', prestate);
                }, 1000);
            }
        })
        if(!story_already_open){
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
        }
    });
    $('#main').on('click', 'h3.complaint-category', function(){
        var symptom = $(this).parent();
        var questionnaires = symptom.find('.complaint-questionnaires');
        questionnaires.toggle("slow");
    });
    $('#main').on('click', '.story-viewer-action-na', function(){
        var na = $(this).attr('data-na');
        if(!na) na = 'shown';
        if(na == 'shown'){
            $('.value-na').closest('.complaint-qa').css('display', 'none');
            $(this).attr('data-na', 'hidden');
        }else{
            $('.value-na').closest('.complaint-qa').css('display', 'inline');
            $(this).attr('data-na', 'shown');
        }
    });
    $('#main').on('click', '.complaint-media-image', function(){
        var src   = $(this).attr('src');
        var title = $(this).prev().html();
        $(this).fancybox({
            'transitionIn'	:	'elastic',
            'transitionOut'	:	'elastic',
            'speedIn'		:	600, 
            'speedOut'		:	200, 
            'href'          :   src,
            'title'   		:   title
        });
    //     var src = $(this).attr('src');
    //     var viewer = ImageViewer();
    //     $('.gallery-items').click(function () {
    //         var imgSrc = src,
    //             highResolutionImage = $(this).data(src);
    
    //         viewer.show(imgSrc, highResolutionImage);
    //     });
    });
    $(document).on('click', "div.story-viewer-print", function(event){
        // var viewer = $($(this).closest('.story-viewer'));
        // var story_id = viewer.data('story');
        // var dialog = bootbox.dialog({
        //     title: 'Print Prescription',
        //     message: 'Loading Prescription ...'
        // });
        // dialog.init(function(){
        //     $.ajax({
        //         url: '/_prescription/'+story_id
        //     }).done(function(content, status, xhr){
        //         var content_length = content.length;
        //         if(content_length){
        //             var story_board = $($.trim(content.replace(/\s+/g, " ")));

        //             var body = dialog.find('.bootbox-body');
        //             body.html(story_board);
        //         }
        //     });            
        // });
    });
});
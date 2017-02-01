$(document).ready(function(){
    $(document).on('click', "div.story-viewer-close", function(event){
        $(this).parent().hide();
    });
});
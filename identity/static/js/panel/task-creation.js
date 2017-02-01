(function($){
    $(document).ready(function(){
        $('#id_when').datetimepicker({
            format:'Y-m-d H:i',
            step: 15,
            inline: true
        });
        $('#task_creation_panel').submit(function(e){
            e.preventDefault();
            var form = $(this).find('form');
            var action = form[0].action;
            //var json = {};
            //form.serializeArray().map(function(x){
            //    json[x.name] = x.value;
            //});
            console.log(action);
            //console.log(json);
            $.ajax({
                type: "POST",
                url: action,
                data: form.serialize(),
                success: function(res){
                    console.log(res);
                    var task_ul = $('#patient-tasks > ul');
                    identity.task.added(res.task, task_ul, function(){
                        
                    }, function(){});
                }
            });
        });
    });
})(jQuery);
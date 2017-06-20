(function($){
    $(document).ready(function(){
        $('.appointment-status-icon').click(function(){
            var appointment_el          = $($(this).parents('.appointment')[0]);
            var appointment_sprite_el   = $($(this).parents('.appointment-sprite')[0]);
            var negotiations_el         = $($(appointment_el).siblings('.negotiations')[0]);
            
            if(negotiations_el.is(':visible')){
                negotiations_el.css('display', 'none')
                appointment_sprite_el.removeClass('appointment-sprite-none');
            }else{
                appointment_sprite_el.addClass('appointment-sprite-none');
                negotiations_el.css('display', 'block')
            }
        });
        // $('.appointments-heading-filter-range > .filter-range').dateRangePicker({
        //     setValue: function(s,s1,s2){
        //         var self = $(this);
                
        //         var from = self.find('.filter-range-from > input[type="text"]');
        //         var to   = self.find('.filter-range-to   > input[type="text"]');
                
        //         from.val(s1);
        //         to.val(s2);
        //     }
        // });
        $('.negotiation-sprite-reply-btn-respond').click(function(){
            var reply_menu = $($(this).parent().children('.negotiation-sprite-reply-menu')[0]);
            if(reply_menu.is(':visible')){
                reply_menu.hide()
                $(this).show();
            }else{
                reply_menu.show()
                $(this).hide();
            }
        });
        $('.negotiation-proposal input[name="when"]').datetimepicker({
            format:'Y-m-d H:i',
            step: 15,
            mask:'9999-19-39 29:59'
        });
        $('.negotiation-sprite-reply-btn-action').click(function(){
            var sprite = $($(this).parents('.negotiation-sprite-create')[0]);
            var when_control = $(sprite.find('input[name="when"]')[0]);
            var appointment_control = $(sprite.find('input[name="appointment"]')[0]);
            var note_control = $(sprite.find('textarea[name="note"]')[0]);
            var status = 'W';
            if($(this).hasClass('negotiation-sprite-reply-btn-fix')){
                status = 'F'
            }else if($(this).hasClass('negotiation-sprite-reply-btn-negotiate')){
                status = 'W'
            }else if($(this).hasClass('negotiation-sprite-reply-btn-cancel')){
                status = 'C'
            }
            $.ajax({
                url: '/negotiation/create/',
                method: 'POST',
                data: {
                    appointment: appointment_control.val(),
                    note: note_control.val(),
                    when: when_control.val(),
                    status: status,
                    csrfmiddlewaretoken: $.cookie('csrftoken')
                },
                success: function(data){
                    if(data.success){
                        //code
                    }else{
                        $('.form-field-error ul').html('')
                        $.each(data.errors, function(key, errors){
                            var error_div = $(sprite.find('.form-field-error-'+key)[0]);
                            var error_ul = error_div.find('ul');
                            console.log(error_div[0]);
                            error_ul.html('')
                            $.each(errors, function(i, error){
                                var li = $("<li>"+error+"</li>");
                                error_ul.append(li);
                            })
                        })
                    }
                }
            })
        })
    })
})(jQuery)

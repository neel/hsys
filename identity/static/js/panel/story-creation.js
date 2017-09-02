Handlebars.registerHelper('ifCond', function (v1, operator, v2, options) {
    switch (operator) {
        case '==':
            return (v1 == v2) ? options.fn(this) : options.inverse(this);
        case '===':
            return (v1 === v2) ? options.fn(this) : options.inverse(this);
        case '<':
            return (v1 < v2) ? options.fn(this) : options.inverse(this);
        case '<=':
            return (v1 <= v2) ? options.fn(this) : options.inverse(this);
        case '>':
            return (v1 > v2) ? options.fn(this) : options.inverse(this);
        case '>=':
            return (v1 >= v2) ? options.fn(this) : options.inverse(this);
        case '&&':
            return (v1 && v2) ? options.fn(this) : options.inverse(this);
        case '||':
            return (v1 || v2) ? options.fn(this) : options.inverse(this);
        default:
            return options.inverse(this);
    }
});
Handlebars.registerHelper('age', function(dob){
    return moment(dob, 'YYYY-MM-DD').fromNow().replace('ago', 'old');
});
(function($){
    var item_div  =  '<div class="patient-item">';
        item_div +=     '<div class="patient-item-pic">';
        item_div +=         '';
        item_div +=     '</div>';
        item_div +=     '<div class="patient-item-info">';
        item_div +=         '<div class="patient-item-name">';
        item_div +=             '{{first_name}} {{last_name}}';
        item_div +=         '</div>';
        item_div +=         '<div class="patient-item-desc">';
        item_div +=             '{{#ifCond sex "==" "M"}}Male{{else}}Female{{/ifCond}} ';
        item_div +=             '{{age dob}}';
        item_div +=         '</div>';
        item_div +=     '</div>';
        item_div += '</div>';
        
    var story_div  = '<li class="ministory-list-item"><div class="ministory"><div class="ministory-sprite" data-id="{{id}}">';
        story_div += '  <div class="ministory-heading">';
        story_div += '      <div class="ministory-doctor">{{doctor}}</div>';
        story_div += '      <div class="ministory-patient">{{patient}}</div>';
        story_div += '      <div class="ministory-when">{{when}}</div>';
        story_div += '  </div>';
        story_div += '  <div class="ministory-body">{{subject}}</div>';
        story_div += '</div></div></li>';
        
    $(document).ready(function(){
//        $('#id_when').datetimepicker({
//            format:'Y-m-d H:i',
//            step: 15,
//            inline: true
//        });
        var patient_engine = new Bloodhound({
            name: 'patient',
            remote: {
                url: '/api/v1/patientcatalog/?format=json&query=%QUERY',
                filter: function(d){
                    return $.map(d.objects, function(patient){
                        patient.full_name = ''+patient.first_name+' '+patient.last_name;
                        return patient;
                    });
                }
            },
            datumTokenizer: function(d){
                return Bloodhound.tokenizers.whitespace(d.val);
            },
            queryTokenizer: Bloodhound.tokenizers.whitespace
        });
        patient_engine.initialize();
        $('#id_patient_selector').typeahead({
            highlight: true
        },{
            source: patient_engine.ttAdapter(),
            displayKey: 'full_name',
            templates: {
                suggestion: Handlebars.compile(item_div)
            }
        }).on('typeahead:selected', function(e, suggestion, name){
            $('#id_patient').val(suggestion.id);
        });        
        $('.story-refer').click(function(){
            var self = $(this);
            console.log($(this).parent());
            var refered = parseInt($('#id_story_referer').val());
            console.log(refered);
            jQuery.get("/api/v1/story/"+refered, function(story){
                var story_template = Handlebars.compile(story_div);
                var story_html = story_template({
                    id: story.id,
                    patient: story.patient.first_name+" "+story.patient.last_name,
                    doctor: story.doctor.first_name+" "+story.doctor.last_name,
                    when: story.when,
                    subject: story.subject
                });
                var story_elem = $($.trim(story_html.replace(/\s+/g, " ")));
                var refered_stories = self.parent().parent().find('ul.ministories-list');
                console.log(refered_stories);
                refered_stories.append(story_elem);

                var option_elem = $('<option value="'+ story.id +'" selected>'+story.subject+'</option>');
                $('#id_refers_to').append(option_elem);
                console.log($('#id_refers_to'), option_elem);
            });
        });
        $('#story_creation_form').submit(function(e){
            e.preventDefault();
            if($('#prescription_body_editor').is(':visible')){
                return;
            }
            var overlay = $('#story_creation_panel .story-creation-form-overlay');
            $('.form-field-error ul').html('');
            overlay.addClass('story-creation-form-overlay-loading');
            $.ajax({
                url:  $(this).attr('action'),
                data: $(this).serializeArray(),
                type: 'POST',
                success: function(data){
                    overlay.removeClass('story-creation-form-overlay-loading');
                    overlay.html('');
                    if(data.success){
                        overlay.addClass('story-creation-form-overlay-success');
                        overlay.html('Successfully Created Appointment');
                        overlay.show();
                        setTimeout(function(){
                            overlay.removeClass('story-creation-form-overlay-success');
                            overlay.html('');
                            overlay.hide();
                            $('#story_creation_button').trigger('click');
                            $('#id_story_referer').val('');
                            $('#id_body').val('{"envelops": []}');
                            $('#prescription').attr('data-prescription', '{"envelops": []}');
                            $('#prescription_body').html('');
                            var panel = $('#story_creation_panel');
                            panel.hide();
                        }, 1500)
                    }else{
                        $.each(data.errors, function(key, errors){
                            var elem = $('#id_'+key);
                            var error_div = $(elem.siblings('.form-field-error')[0]);
                            var error_ul = error_div.find('ul');
                            error_ul.html('')
                            $.each(errors, function(i, error){
                                var li = $("<li>"+error+"</li>");
                                error_ul.append(li);
                            })
                        })
                    }
                    console.log(data);
                },
                error: function(xhr){
                    overlay.removeClass('story-creation-form-overlay-loading');
                    overlay.html('');
                    if(xhr.status == 403){
                        var error_panel =  $('#story_creation_panel .form-error');
                        error_panel.html('You are Not Authorized to Create an Appointment');
                    }
                }
            });
            return false;
        });
        $('#story_creation_reset').click(function(){
            $('#id_refers_to').html('');
            $('#story_creation_panel ul.refered-ministories-list').html('')
            $('#story_creation_button').trigger('click');
            $('#id_story_referer').val('');
            $('#id_body').val('{"envelops": []}');
            $('#prescription').attr('data-prescription', '{"envelops": []}');
            $('#prescription_body').html('');
            var panel = $('#story_creation_panel');
            panel.hide();
        });
    });
})(jQuery);

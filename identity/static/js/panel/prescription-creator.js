function create_prescription(div, story_id, patient_id, patient_name){
    $('#story_creation_reset').trigger('click');
    var story_viewer = $(div).closest('.story-viewer');
    console.log(story_viewer);
    story_viewer.css('left', '0px');
    $('.story-viewer').each(function(){
        if(this != story_viewer[0]) $(this).remove();
    })
    console.log(story_id, patient_id, patient_name);
    var panel = $('#story_creation_panel');
    panel.show();
    $("#id_patient").val(patient_id);
    $("#id_patient_selector").val(patient_name);
    $('#id_story_referer').val(story_id);
    $('.story-refer').trigger("click");
}
var render_prescription_data = function(data, elem, store){
    var json = data;
    var body = elem;
    body.html('');
    $(json.envelops).each(function(){
        var container = $('<div data-id="{0}" data-key="{1}" class="prescription-entry medication-{2} well well-sm">    \
                                <div class="prescription-entry-remove glyphicon glyphicon-remove"></div>                \
                                <div class="prescription-entry-content">                                                \
                                </div>                                                                                  \
                            </div>'.format(this.id, this.type, this.type));
        if(this.type == 'medicine'){
            var elem = $(make_med_text(this.content).text);
            container.find('.prescription-entry-content').append(elem);
        }else if(this.type == 'advice'){
            var elem = $(make_advice_text(this.content));
            container.find('.prescription-entry-content').append(elem);
        }else if(this.type == 'investigation'){
            var elem = make_investigation_text(this.content);
            container.find('.prescription-entry-content').append(elem);
        }else if(this.type == 'remark'){
            var elem = $(make_remark_text(this.content));
            container.find('.prescription-entry-content').append(elem);
        }else if(this.type == 'appointment'){
            var elem = $(make_appointment_text(this.content));
            container.find('.prescription-entry-content').append(elem);
        }
        body.append(container);
    });
    if(store){
        store.val(JSON.stringify(json));
    }
}
var dict = {
    'tablet':       {'bn': 'ট্যাবলেট'},
    'capsule':      {'bn': 'ক্যাপসুল '},
    'ointment':     {'bn': 'মলম'},
    'injection':    {'bn': 'ইনজেকশন '},
    'syrup':        {'bn': 'সিরাপ'},

    'once':         {'bn': 'এক বার'},
    'twice':        {'bn': 'দু বার'},
    'thrice':       {'bn': 'তিন বার'},
    'times':        {'bn': 'বার'},
    'daily':        {'bn': 'দিনে'},
    'everyday':     {'bn': 'প্রতিদিন'},
    'every':        {'bn': 'প্রতি'},
    'day':          {'bn': 'দিন'},
    'days':         {'bn': 'দিন'},

    'before':       {'bn': 'এর আগে'},
    'after':        {'bn': 'এর পরে'},
    'breakfast':    {'bn': 'প্রাতরাশ'},
    'lunch':        {'bn': 'মধ্যাহ্নভোজ'},
    'dinner':       {'bn': 'সান্ধ্যভোজন'},

    'and':          {'bn': 'এবং'}
};
function tr(phrase, lang){
    if(phrase in dict){
        return dict[phrase].bn;
    }
    return phrase;
}
String.prototype.format = function() {
    var formatted = this;
    for( var arg in arguments ) {
        formatted = formatted.replace("{" + arg + "}", arguments[arg]);
    }
    return formatted;
};
/**
 * generates a translatable medicine text for the given medicine object
 */
function make_med_text(medicine){
    var error_text = "";
    function sanity(value, key){
        if(value === undefined || (typeof value == 'string' && !value.length) || (typeof value == 'number' && isNaN(value))){
            if(error_text.length == 0)
                error_text = "<span class='error-input'>Invalid/No {0}</span>".format(key);
            return '';
        }
        return value;
    }
    var str = " <span class='translatable'><span class='tag tag-en tag-active' data-order='1'>{0}</span><span class='tag tag-bn' data-order='1'>{1}</span></span> \
                <span class='translatable'><span class='tag tag-en tag-active' data-order='2'>{2}</span><span class='tag tag-bn' data-order='2'>{3}</span></span></span> \
                <span class='translatable'><span class='tag tag-en tag-active' data-order='3'>{4}</span><span class='tag tag-bn' data-order='3'>{5}</span></span></span> \
                <span class='translatable'><span class='tag tag-en tag-active' data-order='4'>{6}</span><span class='tag tag-bn' data-order='4'>{7}</span></span></span>"
                .format(
                    sanity(medicine.type, "type"), tr(sanity(medicine.type, "type")),
                    sanity(medicine.name, "name"), tr(sanity(medicine.name, "name")),
                    sanity(medicine.dose, "dose"), tr(sanity(medicine.dose, "dose")),
                    sanity(medicine.unit, "unit"), tr(sanity(medicine.unit, "unit"))
                );
    if(sanity(medicine.interval.frequency, "frequency") > 0){
        var freq_text = "";
        switch(sanity(medicine.interval.frequency, "frequency")){
            case 1: 
                freq_text = "<span class='translatable'><span class='tag tag-en tag-active' data-order='5'>{0}</span><span class='tag tag-bn' data-order='6'>{1}</span></span>".format("once", tr("once"));
                break;
            case 2: 
                freq_text = "<span class='translatable'><span class='tag tag-en tag-active' data-order='5'>{0}</span><span class='tag tag-bn' data-order='6'>{1}</span></span>".format("twice", tr("twice"));
                break;
            case 3: 
                freq_text = "<span class='translatable'><span class='tag tag-en tag-active' data-order='5'>{0}</span><span class='tag tag-bn' data-order='6'>{1}</span></span>".format("thrice", tr("thrice"));
                break;
            default: 
                freq_text = "<span class='translatable'><span class='tag tag-en tag-active' data-order='5'  >{0}</span><span class='tag tag-bn' data-order='6'  >{1}</span></span> \
                            <span class='translatable'><span class='tag tag-en tag-active' data-order='5.1'>{2}</span><span class='tag tag-bn' data-order='6.1'>{3}</span></span>"
                .format(
                    sanity(medicine.interval.frequency, 'frequency'), tr(sanity(medicine.interval.frequency, 'frequency')), 
                    "times", tr("times")
                );
        }
        str += freq_text+"<span class='translatable'><span class='tag tag-en tag-active' data-order='6'>{0}</span><span class='tag tag-bn' data-order='5'>{1}</span></span>".format("daily", tr("daily"));
        if(typeof sanity(medicine.interval.days, "days interval") == 'number'){
            var days_interval_text = "";
            switch(medicine.interval.days){
                case 0:
                    days_interval_text = "<span class='translatable'><span class='tag tag-en tag-active' data-order='7'>{0}</span><span class='tag tag-bn' data-order='7'>{1}</span></span>".format("everyday", tr("everyday"));
                    break;
                case 1:
                    days_interval_text = "<span class='translatable'><span class='tag tag-en tag-active' data-order='7'>{0}</span><span class='tag tag-bn' data-order='7'>{1}</span></span>".format("every alternate day", "এক দিন অন্তর");
                    break;
                case 2:
                    days_interval_text = "<span class='translatable'><span class='tag tag-en tag-active' data-order='7'>{0}</span><span class='tag tag-bn' data-order='7'>{1}</span></span>".format("every third day", "২ দিন অন্তর");
                    break;
                default:
                    days_interval_text = "<span class='translatable'><span class='tag tag-en tag-active' data-order='7'>{0}</span><span class='tag tag-bn' data-order='7'>{1}</span></span>".format("every {0}th day".format(medicine.interval.days), "{0} দিন অন্তর".format(tr(medicine.interval.days-1)));
            }
            str += days_interval_text;
        }

        if(medicine.interval.mode == 'clock'){
            if(Array.from(new Set(medicine.interval.clocks)).length != medicine.interval.clocks.length){
                if(error_text.length == 0)
                    error_text = "<span class='error-input'>Duplicate time in schedule</span>";
            }
            if(medicine.interval.clocks.length > 0){
                str += "<span class='translatable'><span class='tag tag-en tag-active' data-order='8'>{0}</span><span class='tag tag-bn' data-order='8.1'>{1}</span></span>".format("on", "এ");
            }
            $(medicine.interval.clocks).each(function(i, v){
                str += "<span class='translatable'><span class='tag tag-en tag-active' data-order='8.1'>{0}</span><span class='tag tag-bn' data-order='8'>{1}</span></span>".format(this, tr(this));
                str += (i == medicine.interval.clocks.length-2) ? "<span class='translatable'><span class='tag tag-en tag-active' data-order='8.1'>{0}</span><span class='tag tag-bn' data-order='8'>{1}</span></span>".format("and", tr("and")) : ((i < medicine.interval.clocks.length-1) ? "<span class='translatable'><span class='tag tag-en tag-active' data-order='8.1'>,</span><span class='tag tag-bn' data-order='8'>,</span></span>" : "");
            });
        }else if(medicine.interval.mode == 'event'){
            if(medicine.interval.event.context.length != medicine.interval.frequency){
                if(error_text.length == 0)
                    error_text = "<span class='error-input'>Expecting {0} doses, marked {1} doses {2}</span>".format(medicine.interval.event.context, medicine.interval.frequency, medicine.interval.event.context.join(' '));
            }
            str += "<span class='translatable'><span class='tag tag-en tag-active' data-order='8'>{0}</span><span class='tag tag-bn' data-order='8.1'>{1}</span></span>".format(sanity(medicine.interval.event.when, "when"), tr(sanity(medicine.interval.event.when, "when")));
            $(medicine.interval.event.context).each(function(){
                str += "<span class='translatable'><span class='tag tag-en tag-active' data-order='8'>{0}</span><span class='tag tag-bn' data-order='8.1'>{1}</span></span>".format(this, tr(this));
            });
        }else{
            if(error_text.length == 0)
                error_text = "<span class='error-input'>Invalid/No mode (clock | event)</span>";
        }

        if(sanity(medicine.termination, "termination") <= 0){
            if(error_text.length == 0)
                error_text = "<span class='error-input'>Termination must be more than 0 days</span>";
        }else{
            str += "<span class='translatable'><span class='tag tag-en tag-active' data-order='9' >{0}</span><span class='tag tag-bn' data-order='11'>{1}</span></span> \
                    <span class='translatable'><span class='tag tag-en tag-active' data-order='10'>{2}</span><span class='tag tag-bn' data-order='9' >{3}</span></span> \
                    <span class='translatable'><span class='tag tag-en tag-active' data-order='11'>{4}</span><span class='tag tag-bn' data-order='10'>{5}</span></span>"
                    .format(
                        "for", "পর্যন্ত", 
                        medicine.termination, tr(medicine.termination),
                        "days", tr("days")
                    );
        }
    }else{
        str += "<span class='translatable'><span class='tag tag-en tag-active' data-order='4'>({0})</span><span class='tag tag-bn' data-order='4'>({1})</span></span></span>"
                .format(medicine.interval.custom, medicine.interval.custom);
    }
    var valid = (error_text.length == 0);
    
    return {
        'valid': valid, 
        'text': "<div class='translatable-compound'> \
                    <div class='translatable-tokens'>{0}</div> \
                    <div class='translation-actions'><div class='translation-action translate-bn'>bn</div><div class='translation-action translate-en'>en</div></div> \
                </div>".format(error_text+str)
        };
}
/**
 * creates a medicine object from the input field inside elem
 */
function make_medicine(elem){
    var medicine = {
        type: '', // tablet | capsule | ointment | injection 
        name: '', // name of the medicine
        dose: 0,  // dose
        unit: '', // unit of dose
        termination: 0, // for how many days
        interval: {
            frequency: '', // numeric | 0 means as needed | -1 means custom
            days: 0, // days interval
            mode: '',    // clock or event
            clocks: [],
            event: {
                context: [], // breakfast | Lunch | Dinner | Anytime
                when: '' // before | after | not applicable 
            },
            custom: ''
        },
        note: '' // some extra notes if required
    };

    medicine.type               = $(elem).find('.medicine-editor-med-type').find('input:radio:checked').val();
    medicine.name               = $(elem).find('.med-name').val();
    medicine.dose               = parseInt($(elem).find('.med-dose').val());
    medicine.unit               = $(elem).find('.med-dose-unit').attr('data-unit');
    medicine.termination        = parseInt($(elem).find('.med-termination').val());
    medicine.interval.frequency = parseInt($(elem).find('.medicine-editor-med-frequency').attr('data-freq'));
    medicine.interval.days      = parseInt($(elem).find('.med-days').attr('data-interval'));
    medicine.interval.mode      = $(elem).find('.medication-mode').attr('data-mode');
    medicine.interval.custom    = $(elem).find('.med-usecase').val();

    medicine.interval.clocks    = [];
    var clocksv = $(elem).find('.med-timmed-clocks')[0];
    var clocks = $(clocksv).find('.med-clock');
    $(clocks).each(function(){
        var input = $(this).find('input');
        var time = $(input).val();
        medicine.interval.clocks.push(time);
    });

    var contexts = $(elem).find('.med-when-context').find('input:checkbox:checked');
    var ctxs = [];
    $(contexts).each(function(){
        ctxs.push($(this).val());
    });
    medicine.interval.event.when = $(elem).find('.med-when-ba').find('input:radio:checked').val();
    medicine.interval.event.context = ctxs;

    var summary = make_med_text(medicine);
    $(elem).find('.medicine-editor-med-okay').prop("disabled", !summary.valid);
    $(elem).find('.medicine-text').html(summary.text);

    return medicine;
}

function make_investigation_text(investigation){
    var bread = $('<ol class="breadcrumb"></ol>');
    $(investigation.hierarchy).each(function(){
        bread.append($('<li><a href="#">{0}</a></li>'.format(this.category)));
    });
    var note = $('<div class="note">{0}</div>'.format(investigation.note));
    var container = $('<div class="investigation-container"></div>');
    container.append(bread);
    container.append(note);
    return container;
}

function make_advice_text(advice){
    return $('<div class="advice-container">{0}</div>'.format(advice.advice));
}
function make_remark_text(remark){
    return $('<div class="remark-container">{0}</div>'.format(remark.remark));
}
function make_appointment_text(appointment){
    return $('<div class="appointment-block">Appointment fixed on {0} ({1})</div>'.format(appointment.when, appointment.note));
}
$(document).ready(function(){
    Array.prototype.removeValue = function(name, value){
        var array = $.map(this, function(v,i){
            return v[name] === value ? null : v;
        });
        this.length = 0; //clear original array
        this.push.apply(this, array); //push all elements except the one we want to delete
    }
    var make_envelop = function(type, data){
        return {id: (+new Date)+Math.random(), type: type, content: data};
    }
    var save_envelop = function(envelop){
        var prescription = $("#prescription");
        var pdata = JSON.parse(prescription.attr("data-prescription"));
        pdata["envelops"].push(envelop);
        prescription.attr("data-prescription", JSON.stringify(pdata));
    }
    var render_prescription = function(){
        var prescription = $("#prescription");
        var json = JSON.parse(prescription.attr("data-prescription"));
        var body = $("#prescription_body");
        body.html('');
        $(json.envelops).each(function(){
            var container = $('<div data-id="{0}" data-key="{1}" class="prescription-entry medication-{2} well well-sm">    \
                                    <div class="prescription-entry-remove glyphicon glyphicon-remove"></div>                \
                                    <div class="prescription-entry-content">                                                \
                                    </div>                                                                                  \
                               </div>'.format(this.id, this.type, this.type));
            if(this.type == 'medicine'){
                var elem = $(make_med_text(this.content).text);
                container.find('.prescription-entry-content').append(elem);
            }else if(this.type == 'advice'){
                var elem = $(make_advice_text(this.content));
                container.find('.prescription-entry-content').append(elem);
            }else if(this.type == 'investigation'){
                var elem = make_investigation_text(this.content);
                container.find('.prescription-entry-content').append(elem);
            }else if(this.type == 'remark'){
                var elem = $(make_remark_text(this.content));
                container.find('.prescription-entry-content').append(elem);
            }else if(this.type == 'appointment'){
                var elem = $(make_appointment_text(this.content));
                container.find('.prescription-entry-content').append(elem);
            }
            body.append(container);
        });
        $("#id_body").val(JSON.stringify(json));
    }
    $("#prescription_body").on('click', 'div.prescription-entry div.prescription-entry-remove', function(){
        var parent = $(this).parent();
        var id = parent.data('id');
        var prescription = $("#prescription");
        var json = JSON.parse(prescription.attr("data-prescription"));
        json['envelops'].removeValue('id', id);
        prescription.attr("data-prescription", JSON.stringify(json));
        $("#id_body").val(JSON.stringify(json));
        render_prescription();
        console.log(json);
    });
    $("#periodic_medication").click(function(){
        medicine_autocomplete = function(elem){
            var medicine_div = '<div class="autocomplete-suggestion med-suggestion-item" data-kind="{{kind}}" data-name="{{name}}" data-dose="{{dose}}" data-unit="{{unit}}"> \
                                    <span class="med-suggestion-item-specs med-suggestion-kind">{{kind}}</span> \
                                    <span class="med-suggestion-item-specs med-suggestion-name">{{name}}</span> \
                                    <span class="med-suggestion-item-specs med-suggestion-dose">{{dose}}</span> \
                                    <span class="med-suggestion-item-specs med-suggestion-unit">{{unit}}</span> \
                                </div>';
            new autoComplete({
                selector: elem[0],
                minChars: 1,
                source: function(term, response){
                    $.getJSON('/api/v1/medicine/', { query: term }, function(data){
                        var medicines = [];
                        $(data.objects).each(function(){
                            var kind  = this.kind;
                            var doses = this.doses;
                            var name  = this.name;
                            var unit  = this.unit;
                            $(doses).each(function(){
                                medicines.push({
                                    kind: kind,
                                    name: name,
                                    dose: this,
                                    unit: unit
                                });
                            });
                        });
                        response(medicines);
                    });
                },
                renderItem: function (item, search){
                    console.log(item, search);
                    return Handlebars.compile(medicine_div)(item)
                },
                onSelect: function(e, term, item){
                    elem.val(item.getAttribute('data-name'));
                    elem.parent().find('.med-dose').val(item.getAttribute('data-dose'));
                    elem.parent().find('.med-dose-unit').attr('data-unit', item.getAttribute('data-unit'));
                    elem.parent().find('.med-dose-unit').find('.dropdown-toggle').html("Unit ("+item.getAttribute('data-unit')+') <span class="caret"></span>');
                    var type_buttons = elem.parent().parent().find('.medicine-editor-med-type').find('input[type=radio]');
                    type_buttons.each(function(){
                        if($(this).val() == item.getAttribute('data-kind')){
                            $(this).trigger('click');
                        }
                    })
                    // alert('Item "'+item.getAttribute('data-name')+' ('+item.getAttribute('data-dose')+')" selected by '+(e.type == 'keydown' ? 'pressing enter' : 'mouse click')+'.');

                    var editor = $(elem).closest('.editor-panel');
                    make_medicine(editor);
                }
            });
        }
        $('#prescription_body_editor').html('');
        $('#prescription_body_editor').append($($('#snippet_medication_periodic').html()));
        $('#prescription_body_editor').css('display', 'block');

        medicine_autocomplete($('#prescription_body_editor .med-name'));
    });
    $("#test_medication").click(function(){
        $('#prescription_body_editor').html('');
        $('#prescription_body_editor').append($($('#snippet_investigation').html()));
        $('#prescription_body_editor').css('display', 'block');

        var investigation_data = {
            category: 'investigation',
            subcategories: [{
                    category: 'Pathology',
                    subcategories: [{
                        category: 'Blood',
                        subcategories: [{
                            category: 'CBC'
                        },{
                            category: 'Suger'
                        },{
                            category: 'LFT'
                        },{
                            category: 'Lipid Profile'
                        },{
                            category: 'TSH'
                        }]
                    },{
                        category: 'Urine',
                        subcategories: [{
                            category: 'RE'
                        },{
                            category: 'ME'
                        },{
                            category: 'C/S'
                        }]
                    },{
                        category: 'Stool',
                        subcategories: [{
                            category: 'RE'
                        },{
                            category: 'ME'
                        },{
                            category: 'OBT'
                        }]
                    }]
                },{
                    category: 'Radiology',
                    subcategories: [{
                        category: 'X-Ray'
                    },{
                        category: 'USG'
                    },{
                        category: 'CT'
                    },{
                        category: 'MR'
                    },{
                        category: 'Other'
                    }]
                },{
                    category: 'Cardiology',
                    subcategories: [{
                        category: 'ECG'
                    }]
                },{
                    category: 'Nemology'
                },{
                    category: 'Gastro'
                }
        ]};
        var decorate = function(node){
            nchildren = (node.subcategories) ? node.subcategories.length : 0;
            node.elem = $('<a class="list-group-item list-group-item investigation-item">{0}{1}</a>'.format(node.category, nchildren > 0 ? '<span class="badge">{0}</span>'.format(nchildren) : ''));
            if(!nchildren){
                node.elem.addClass('investigation-item-leaf');
            }
            return node.elem;
        }
        var decorate_list = function(nodes){
            var elem = $('<div class="list-group investigation-list">');
            for(i in nodes){
                if(nodes.hasOwnProperty(i)){
                    elem.append(decorate(nodes[i]));
                }
            }
            return elem;
        }
        var collapse = function(node){
            node.elem.removeClass('active');
            var children = node.children;
            children.css('display', 'none');
            if(node.subcategories.length > 0){
                for(i in node.subcategories){
                    if(node.subcategories.hasOwnProperty(i)){
                        collapse(node.subcategories[i]);
                    }
                }
            }
        }
        var c = 0;
        var travarse = function(node, visitor){
            node.id = c++;
            if(node.subcategories === undefined){
                node.subcategories = [];
            }
            var decoration = decorate_list(node.subcategories);
            node.children = decoration;
            if(node.elem){
                $(node.elem).click(function(){
                    for(i in node.siblings){
                        if(node.siblings.hasOwnProperty(i)){
                            collapse(node.siblings[i]);
                        }
                    }
                    node.elem.addClass('active');
                    visitor(node);
                });
            }
            var counter = 0;
            if(node.subcategories.length > 0){
                for(i in node.subcategories){
                    if(node.subcategories.hasOwnProperty(i)){
                        node.subcategories[i].parent = node;
                        node.subcategories[i].siblings = node.subcategories;
                        counter++;
                        travarse(node.subcategories[i], visitor);
                    }
                }
            }
            node.leaf = (counter == 0);
            node.nchildren = counter;
            if(node.elem){
                node.elem.attr('data-id', node.id);
                node.elem.attr('data-leaf', node.leaf);
                node.elem.attr('data-nchildren', node.nchildren);
            }
            return decoration;
        }
        var decoration = travarse(investigation_data, function(node){
            node.children.css('display', 'block');
            if(node.leaf){
                var ancestors = [];
                var pointer = node;
                while(pointer !== undefined){
                    ancestors.push(pointer);
                    pointer = pointer.parent;
                }
                ancestors.reverse();
                ancestors.shift();
                var messagebox = $('<div class="message-box"></div>');
                var bread = $('<ol class="breadcrumb"></ol>');
                $(ancestors).each(function(){
                    bread.append($('<li><a href="#">{0}</a></li>'.format(this.category)));
                });
                messagebox.append(bread);
                messagebox.append('<div class="input-group">                                                        \
                    <span class="input-group-addon" id="sizing-addon1">Note</span>                                  \
                    <input type="text" class="form-control message-box-note" placeholder="note" aria-describedby="sizing-addon1">    \
                </div>');
                
                var dialog = bootbox.dialog({
                    title: 'Additional details (if necessary)',
                    message: messagebox,
                    buttons: {
                        cancel: {
                            label: "Discard",
                            className: 'btn-danger',
                            callback: function(){
                                
                            }
                        },ok: {
                            label: "Save",
                            className: 'btn-success',
                            callback: function(){
                                var note = dialog.find('.bootbox-body').find('.message-box-note').val();
                                var categories = [];
                                $(ancestors).each(function(){
                                    categories.push({category: this.category});
                                })
                                var investigation = {
                                    hierarchy: categories,
                                    note: note
                                }
                                var envelop = make_envelop('investigation', investigation);
                                save_envelop(envelop);
                                console.log(envelop);
                                $('#prescription_body_editor').html('');
                                $('#prescription_body_editor').css('display', 'none');
                                render_prescription();
                            }
                        }
                    }
                });
            }else{
                $('#prescription_body_editor').find('.investigation-container').append(node.children);
            }
        });
        $('#prescription_body_editor').find('.investigation-container').append(decoration);
    });
    $("#advice_medication").click(function(){
        bootbox.prompt({
            title: "Advice to Patient",
            inputType: 'textarea',
            callback: function (result){
                var advice = {advice: result};
                var envelop = make_envelop('advice', advice);
                save_envelop(envelop);
                render_prescription();
            }
        });
    });
    $("#remark_medication").click(function(){
        bootbox.prompt({
            title: "Remarks",
            inputType: 'textarea',
            callback: function (result){
                var advice = {remark: result};
                var envelop = make_envelop('remark', advice);
                save_envelop(envelop);
                render_prescription();
            }
        });
    });

    /* medicine { */
    $("#prescription_body_editor").on('click', "ul.med-freq-selector li", function(){
        var freq = parseInt($(this).attr('data-freq'));
        var freq_row = $(this).closest('.frequency-row');
        $(freq_row).find(".medication-mode").attr('data-freq', freq);
        $(freq_row).find(".medication-mode").attr('data-mode', '');
        $(freq_row).find('.medicine-editor-med-frequency').attr('data-freq', freq);
        $(freq_row).find('.medicine-editor-med-frequency').html('Frequency ('+freq+') <span class="caret"></span>');

        $(freq_row).find('.med-timmed-clocks').html('');
        $(freq_row).find('.med-timmed-clocks').css('display', 'none');
        $(freq_row).find('.med-event').css('display', 'none');
        $(freq_row).find('.med-asneeded')[0].style.setProperty('display', 'none', 'important');
        $(freq_row).find(".medication-mode").css('display', 'none');
        console.log(freq);
        if(freq > 0){
            $(freq_row).find(".medication-mode").css('display', 'block');
            $(freq_row).parent().find(".med-termination").removeAttr('disabled');
            $(freq_row).find('.med-days').find('.dropdown-toggle').removeClass('disabled');
        }else if(freq == 0){
            $(freq_row).find('.med-asneeded')[0].style.setProperty('display', 'inline-table', 'important');
            $(freq_row).parent().find(".med-termination").attr('disabled', 'disabled');
            $(freq_row).find('.med-days').find('.dropdown-toggle').addClass('disabled');
        }
        var editor = $(this).closest('.editor-panel');
        make_medicine(editor);
    });
    $("#prescription_body_editor").on('click', ".med-dose-unit ul.dropdown-menu li", function(){
        var unit = $(this).closest('.med-dose-unit');
        unit.attr('data-unit', $(this).attr('value'));
        unit.find('.dropdown-toggle').html("Unit ("+unit.attr('data-unit')+') <span class="caret"></span>');

        var editor = $(this).closest('.editor-panel');
        make_medicine(editor);
    });
    $("#prescription_body_editor").on('click', ".med-days ul.dropdown-menu li", function(){
        var unit = $(this).closest('.med-days');
        unit.attr('data-days', $(this).attr('value'));
        unit.attr('data-interval', $(this).attr('data-interval'));
        unit.find('.dropdown-toggle').html("Days ("+unit.attr('data-days')+') <span class="caret"></span>');

        var editor = $(this).closest('.editor-panel');
        make_medicine(editor);
    });
    $("#prescription_body_editor").on('change', '.medicine-editor-med-type .btn input', function(){
        var editor = $(this).closest('.editor-panel');
        make_medicine(editor);
    });
    $("#prescription_body_editor").on('change', '.med-when-ba .btn input', function(){
        var editor = $(this).closest('.editor-panel');
        make_medicine(editor);
    });
    $("#prescription_body_editor").on('change', '.med-when-context .btn input', function(){
        var editor = $(this).closest('.editor-panel');
        make_medicine(editor);
    });
    $('#prescription_body_editor').on('click', '.med-mode-timmed', function(){
        var template = $($('.med-timmed-clock-template')[0]).html();
        var form = $(this).parent().parent().parent();
        var freq = parseInt($(this).parent().parent().attr('data-freq'));
        $(form).find('.med-timmed-clocks').html('');
        for(var i =0; i< freq; ++i){
            $(form).find('.med-timmed-clocks').append($(template));
        }
        $(form).find('.med-timmed-clocks').css('display', 'block');
        $(this).parent().parent().css('display', 'none');
        $(this).parent().parent().attr('data-mode', 'clock');
        $('.clockpicker').clockpicker();

        var editor = $(this).closest('.editor-panel');
        make_medicine(editor);
    });
    $('#prescription_body_editor').on('click', '.med-mode-event', function(){
        var med_event = $(this).closest('.form-inline').find('.med-event')[0];
        med_event.style.setProperty('display', 'inline-table', 'important');
        $(this).parent().parent().css('display', 'none');
        $(this).parent().parent().attr('data-mode', 'event');

        var editor = $(this).closest('.editor-panel');
        make_medicine(editor);
    });
    $('#prescription_body_editor').on('keyup', '.med-name', function(){
        var editor = $(this).closest('.editor-panel');
        make_medicine(editor);
    });
    $('#prescription_body_editor').on('keyup', '.med-termination', function(){
        var editor = $(this).closest('.editor-panel');
        make_medicine(editor);
    });
    $('#prescription_body_editor').on('keyup', '.med-dose', function(){
        var editor = $(this).closest('.editor-panel');
        make_medicine(editor);
    });
    $('#prescription_body_editor').on('keyup', '.med-usecase', function(){
        var editor = $(this).closest('.editor-panel');
        make_medicine(editor);
    });
    $('#prescription_body_editor').on('propertychange change keyup paste input', 'div.med-timmed-clocks .med-clock', function(){
        var editor = $(this).closest('.editor-panel');
        make_medicine(editor);
    });
    $('#prescription_body_editor, #prescription_body, #main').on('click', '.translate-bn', function(){
        var container = $(this).closest('.translatable-compound').find('.translatable-tokens');
        $(container).find('.translatable > .tag-active').removeClass('tag-active');
        $(container).find('.translatable > .tag-bn').addClass('tag-active');
        var tokens = $(container).find('.translatable');
        tokens.each(function(i,v){
            $(this).attr('data-index', i);
        });
        tokens.sort(function(a,b){
            var order_a = parseFloat($(a).find('.tag-active').attr('data-order'));
            var order_b = parseFloat($(b).find('.tag-active').attr('data-order'));
            var delta = order_a - order_b;
            if(delta == 0){
                return parseInt($(a).attr('data-index')) - parseInt($(b).attr('data-index'));
            }
            return delta;
        });
        container.html('');
        container.append(tokens);
    });
    $('#prescription_body_editor, #prescription_body, #main').on('click', '.translate-en', function(){
        var container = $(this).closest('.translatable-compound').find('.translatable-tokens');
        $(container).find('.translatable > .tag-active').removeClass('tag-active');
        $(container).find('.translatable > .tag-en').addClass('tag-active');
        var tokens = $(container).find('.translatable');
        tokens.each(function(i,v){
            $(this).attr('data-index', i);
        });
        tokens.sort(function(a,b){
            var order_a = Math.round(parseFloat($(a).find('.tag-active').attr('data-order'))*10);
            var order_b = Math.round(parseFloat($(b).find('.tag-active').attr('data-order'))*10);
            var delta = order_a - order_b;
            if(delta == 0){
                return parseInt($(a).attr('data-index')) - parseInt($(b).attr('data-index'));
            }
            return delta;
        });
        container.html('');
        container.append(tokens);
    });
    $('#prescription_body_editor').on('click', '.medicine-editor-med-okay', function(){
        var editor = $(this).closest('.editor-panel');
        var medicine = make_medicine(editor);
        var envelop = make_envelop('medicine', medicine);
        save_envelop(envelop);
        $('#prescription_body_editor').html('');
        $('#prescription_body_editor').css('display', 'none');
        render_prescription();
    });
    $('#prescription_body_editor').on('click', '.medicine-editor-med-cancel', function(){
        $('#prescription_body_editor').html('');
        $('#prescription_body_editor').css('display', 'none');
    });
    /* } medicine */
    $("#appointment_medication").click(function(){
        $('#prescription_body_editor').html('');
        $('#prescription_body_editor').append($($('#snippet_appointment').html()));
        $('#prescription_body_editor').css('display', 'block');

        $('#prescription_body_editor .appointment-when').datetimepicker({
            format:'Y-m-d H:i'
        });
    });
    $('#prescription_body_editor').on("click", ".appointment-container .medicine-editor-appointment-cancel", function(){
        $('#prescription_body_editor').html('');
        $('#prescription_body_editor').css('display', 'none');
    });
    $('#prescription_body_editor').on("click", ".appointment-container .medicine-editor-appointment-okay", function(){
        var container = $(this).closest('.appointment-container');
        var when = container.find('.appointment-when').val();
        var note = container.find('.appointment-note').val();
        var envelop = make_envelop('appointment', {
            when: when,
            note: note
        });
        save_envelop(envelop);
        $('#prescription_body_editor').html('');
        $('#prescription_body_editor').css('display', 'none');
        render_prescription();
    });
});

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
    return moment(dob, 'YYYY-MM-DD').fromNow().replace('ago', 'old')
});
(function($){
    var item_div =  '<div class="doctor-item">';
        item_div +=     '<div class="doctor-item-pic">';
        item_div +=         '';
        item_div +=     '</div>'
        item_div +=     '<div class="doctor-item-info">';
        item_div +=         '<div class="doctor-item-name">';
        item_div +=             'Dr. {{first_name}} {{last_name}}';
        item_div +=         '</div>';
        item_div +=         '<div class="doctor-item-desc">';
        item_div +=             '{{#ifCond sex "==" "M"}}Male{{else}}Female{{/ifCond}} '
        item_div +=             '{{age dob}}'
        item_div +=         '</div>';
        item_div +=     '</div>';
        item_div += '</div>';
    $(document).ready(function(){
        $('#id_schedule').datetimepicker({
            format:'Y-m-d H:i',
            step: 15,
            inline: true
        });
        var doctor_engine = new Bloodhound({
            name: 'doctors',
            remote: {
                url: '/api/v1/doctorcatalog/?format=json&query=%QUERY',
                filter: function(d){
                    return $.map(d.objects, function(doctor){
                        doctor.full_name = 'Dr. '+doctor.first_name+' '+doctor.last_name;
                        return doctor;
                    });
                }
            },
            datumTokenizer: function(d){
                return Bloodhound.tokenizers.whitespace(d.val);
            },
            queryTokenizer: Bloodhound.tokenizers.whitespace
        });
        doctor_engine.initialize();
        $('#id_doctor_selector').typeahead({
            highlight: true
        },{
            source: doctor_engine.ttAdapter(),
            displayKey: 'full_name',
            templates: {
                suggestion: Handlebars.compile(item_div)
            }
        }).on('typeahead:selected', function (e, suggestion, name) {
            $('#id_doctor').val(suggestion.id);
        });
    })
})(jQuery)

(function($){
    $(document).ready(function(){
        $('.admissions-heading-filter-range > .filter-range').dateRangePicker({
            setValue: function(s,s1,s2){
                var self = $(this);
                
                var from = self.find('.filter-range-from > input[type="text"]');
                var to   = self.find('.filter-range-to   > input[type="text"]');
                
                from.val(s1);
                to.val(s2);
            }
        })
    })
})(jQuery)
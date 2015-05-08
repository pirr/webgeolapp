var selected_pis;
var selected_sources;

$('#sources_type').multiselect({
    includeSelectAllOption: true,
    enableFiltering: true,
    filterBehavior: 'text',
    filterPlaceholder: 'Найти',
    buttonWidth: '200px',
    nonSelectedText: 'Выбрать источник',
    selectAllText: 'Выбрать все',
    allSelectedText: 'Все источники',
    maxHeight: 300,
    checkboxName: 'multiselect[]',
    onChange: function(source, checked) {
        var sources = $('#sources_type option:selected');
        selected_sources = [];
        $(sources).each(function(index, source){
            selected_sources.push($(this).val());
        });
    }
});



$('#pis').multiselect({
    numberDisplayed: 0,
    includeSelectAllOption: true,
    enableFiltering: true,
    filterBehavior: 'text',
    filterPlaceholder: 'Найти',
    buttonWidth: '50px',
    buttonText: function(options, select) {
                if (options.length >= 0) {
                    return 'ПИ';
                }
            },
    nonSelectedText: 'Выбрать ПИ',
    selectAllText: 'Выбрать все',
    allSelectedText: 'Все ПИ',
    maxHeight: 300,
    checkboxName: 'multiselect[]',
    onChange: function(pi, checked) {
        var pis = $('#pis option:selected');
        selected_pis = [];
        $(pis).each(function(index, pi){
            selected_pis.push($(this).val());
        });
    }
});

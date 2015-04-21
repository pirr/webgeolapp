function login(){
    user = $('#user').val();
    password = $('#password').val();
    console.log(JSON.stringify({user:user, password:password}));
    $.ajax({
        url: '/login',
        data: JSON.stringify({user:user, password:password}),
        success: function(response) {
            if (response=='Err') 'Err';
            else location.reload(); 
        }
    })     
};

function logout() {
    $.ajax( {
        url: '/logout',
        success: function(response) {
            location.reload();
        }
    });
}

// $(document).ready(function(){
//     $('#search').click()
// });

function search(){
    searchname = $('#searchname').val();
    $.ajax({
        url: '/search',
        data: JSON.stringify({'searchname': searchname}),
        success: function(response) {
            console.log(response);
            $('#search_results').html(response.html)
        }
    });
}

// function open_url(url){
//     window.open(url, '_blank');
// }

function html_response(url, id){
$(document).ready( function() {
    $.ajax({
        url: url,
        success: function(response) {
            console.log(response);
            $(id).html(response.html)
        }
    });
}); 
}

$('#doc_tabs a').click(function (e) {
    e.preventDefault();
  
    var url = $(this).attr("data-url");
    var href = this.hash;
    var pane = $(this);
    
    // ajax load from data-url
    $(href).load(url,function(result){      
        pane.tab('show');
    });
});
// load first tab content
$('#doc_about').load($('.active a').attr("data-url"),function(result){
  $('.active a').tab('show');
});
// load first tab content
$('#home').load($('.active a').attr("data-url"),function(result){
  $('.active a').tab('show');
});

$(document).ready( function() {
    jQuery.ajaxSetup( {
        type:'POST', 
        contentType: 'application/json',
        async: true, 
    });
    //active class navbar button
    var url = window.location;
        $('ul.nav a[href="" + url + ""]').parent().addClass('active');
        $('ul.nav a').filter(function() {
             return this.href == url;
        }).parent().addClass('active');
   
});
    

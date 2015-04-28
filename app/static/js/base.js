function login(){
    user = $('#user').val();
    password = $('#password').val();
    // console.log(JSON.stringify({user:user, password:password}));
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

function search(url){
    searchname = $('#searchname').val();
    $.ajax({
        url: url,
        data: JSON.stringify({'searchname': searchname}),
        success: function(response) {
            console.log(response);
            $('#search_results').html(response.html)
        }
    });
}

function open_url(url) {
    window.open(url, '_blank');
}

function open_url_self(url) {
    window.open(url, '_self');
}

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
    

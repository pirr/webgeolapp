function login() {
    user = $('#user').val();
    password = $('#password').val();
    console.log(JSON.stringify({user:user, password:password}));
    $.ajax({
        url: '/login',
        data: JSON.stringify({user:user, password:password}),
        success: function(response) {
            if (response=='Err');
            else location.reload(); 
        }
    })     
}

function logout() {
    $.ajax( {
        url: '/logout',
        success: function(response) {
            location.reload();
        }
    });
}

function checkdoc(but) {
    var check = but.getAttribute('value');
    console.log(JSON.stringify({check:check}));
    $.ajax({
        url: '/checkdoc',
        data: JSON.stringify({check:check}),
    })
    .done(function(data){

    });
    return data
}

//active class navbar button
$(document).ready(function () {
        var url = window.location;
        $('ul.nav a[href="" + url + ""]').parent().addClass('active');
        $('ul.nav a').filter(function() {
             return this.href == url;
        }).parent().addClass('active');
    });

$(document).ready( function() {
    jQuery.ajaxSetup( {
        type:'POST', 
        contentType: 'application/json',
        async: true, 
    });
    
} )
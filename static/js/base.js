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
};

function logout() {
    $.ajax( {
        url: '/logout',
        success: function(response) {
            location.reload();
        }
    });
}

function openurl(url) {
    window.open(url, '_blank');
}

$(document).ready(function($) {
    $(".clickable-row").click(function() {
        window.open($(this).data("href"), '_blank')
    });
});

// $(document).ready(function() {
//     $('button').click(function(){
//             url: '/documents'
//         var check = $(this).prop('value');
//         $.ajax({
//             url: '/checkdoc/',
//             data: JSON.stringify({check:check}),
//             success: function(data) {
//             console.log(JSON.stringify({check:check}))
//             return data;
//         }
//         });
//     });
//     });

// $(document).ready( function() {
//     $('#test').each(function(){
//         $('#test').click(function(){
//             console.log($(this).val());
//     });
// });
// });

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
    
});

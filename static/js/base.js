function login() {
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

function search() {
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

<<<<<<< HEAD
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
=======
function open_url(url){
    window.open(url, '_blank');
}
>>>>>>> 751610120d0f3ff750ecbc9101bb2ca2a5007739

function docs_in_objs_response(url, id){
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
    

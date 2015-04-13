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

<<<<<<< HEAD
// function checkdoc(but) {
//     var check = but.getAttribute('value');
//     console.log(JSON.stringify({check:check}));
//     $.ajax({
//         url: '/checkdoc',
//         data: JSON.stringify({check:check}),
//         success: function(data) {
//             return data;
//         }
//     });
   
// }
=======
function openurl(url) {
    window.open(url, '_blank');
}
>>>>>>> 3dc9c0dd881b5af912ce4b0ec4562f0c2eb8b8a5

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
function openurl(url) {
    window.open(url, '_blank')
    }

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

function login() {
    user = $('#user').val();
    password = $('#password').val();
    console.log(JSON.stringify({user:user, password:password}));
    $.ajax( {
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

function checkdoc(a) {
    var check = a.getAttribute('value');
    $.ajax({
        url: '/workspacedoc',
        data: JSON.stringify(check),
        success: function(response) {
            console.log(check);
            location.reload();
        }
    })
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


// <script type=text/javascript>
//   $(function() {
//     $('a#calculate').bind('click', function() {
//       $.getJSON($SCRIPT_ROOT + '/_add_numbers', {
//         a: $('input[name="a"]').val(),
//         b: $('input[name="b"]').val()
//       }, function(data) {
//         $("#result").text(data.result);
//       });
//       return false;
//     });
//   });
// </script>
// <h1>jQuery Example</h1>
// <p><input type=text size=5 name=a> +
//    <input type=text size=5 name=b> =
//    <span id=result>?</span>
// <p><a href=# id=calculate>calculate server side</a>
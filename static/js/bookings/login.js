$(function(){
    $('#staff-login-form').on('submit', function(event){
        event.preventDefault();
        console.log('form submitted');
        login()
    });
});

function login(){
    var email = $('#staff-login-email').val();
    var password = $('#staff-login-password').val();
    var studio = $('#staff-login-home-studio').val();

    var bad_request = 400;
    var success_request = 200;

    $.ajax({
        url : '../studios/login',
        type : 'POST',
        data : { email : email, password : password, studios : studio},

        // handle a successful response
        success : function(json) {
            if(json.code == bad_request){
                $('<div class="alert alert-danger" role="alert">' + json.message +'</div>').hide().prependTo('#staff-login-form').slideDown();
            } else if(json.code == success_request){
                window.location.href = '.'
            }
            console.log(json); // log the returned json to the console
            console.log("success"); // another sanity check
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    })
}
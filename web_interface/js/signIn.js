//date: September 2017
//author: rms-dev
//
//
//BEGIN: Refreshing the modal in case any parsley class attributes remain while user logins

var current_login = null;


function initiateSignInModal(event) {
    var $signUpForm = document.getElementById("signUpForm");
    for (i = 0; i < $signUpForm.length; i++) {
        if ($signUpForm.elements[i].classList.contains("form-control")) {
            $signUpForm.elements[i].className = "form-control";
            $signUpForm.elements[i].value = "";
        }
    }
    $('.parsley-errors-list').remove();
    $('.form-control').value = '';
    $(this).find('form').trigger('reset');

    $('#signInPassword').keyup(function(e)  {
        if(e.keyCode == 13)
            signInSubmitControl(e);
    });

    //END: Refreshing the modal

    // BEGIN: Populating the country codes -------------
    // RMS: Change the default country in this code block if required.
    // RMS: Update country-codes.json for correcting erroneous entries, if any.
    $.getJSON("./divs/signIn/country-codes.json", function (data) {
        var $selectCountry = $("#signUpCountry");
        var countryNames = [];
        $selectCountry.empty();
        $.each(data, function (idx, entry) {
            if (entry.name === 'France') {
                $selectCountry.append("<option selected='selected'>" + entry.name + "</option>");
            }
            else {
                $selectCountry.append("<option>" + entry.name + "</option>");
            }
        });
    });

    $('#signInModal').show();
    // END: Populating the country codes -------------
}


function registerUser(event = '') {
    if (event.type === 'click') {
        event.preventDefault();
        var userAccountValues = {}; // dictionary of all values input by user
        var $modalForm = document.getElementById("signInModal");
        var formInstance = $('#signUpForm').parsley();

        formInstance.on('form:validated', function () {
            console.log("In form:validated function");
            ok = $('.parsley-error').length === 0;
            $('.bs-callout-info').toggleClass('hidden', !ok);
            $('.bs-callout-warning').toggleClass('hidden', ok);
        });

        var formValidated = formInstance.validate();
        if (formValidated) {
            var fieldsObj = formInstance.fields;
            if (fieldsObj.length > 0) {
                fieldsObj.forEach(function (fieldIdx) {
                    userAccountValues[fieldIdx.element.name] = fieldIdx.value;
                });
	          }
            else {
                console.log("ERROR: Form fields are empty");
            } //checking for empty fields

            delete userAccountValues['signUpConfirmPassword'];
            delete userAccountValues['signInCGU'];

            //begin client-side hashing using crypto.js library
            let login = userAccountValues['login'];
            let password = userAccountValues['password'];
            let hashed_sha256 = CryptoJS.SHA256(password);
            let client_hashed = hashed_sha256.toString(CryptoJS.enc.Base64);
            userAccountValues['password'] = client_hashed;
            // console.log(userAccountValues); //after password hashing

            //begin request calls for websocket
            sakura.apis.hub.users.create(userAccountValues).then(
                function (wsResult) {
                    if (wsResult) {
                        userAccountValues = {};
        	    		      alert("'"+login + "' has been registered");
                        $('#signInModal').on('hidden.bs.modal', function () {
        	    			        $(this).find('form').trigger('reset');
                        });
        	    		      $("#signInModal").modal("hide");
                        signInSubmitControl(event, login, password)
        	    		      return;
        	    	    }
                    else {
                        console.log("Error callbacks in the new_user function need to be handled properly");
        	    		      return;
                    }
                }).catch(
                function (error_message) {
            	      alert(error_message);
                    if (DEBUG) console.log("E3", error_message);
                });
        }
        else {
            console.log("Form validation failed");
        }
    } // end if click
}

function signInSubmitControl(event, login, passw) {
    if (event.type === 'click' || event.keyCode == 13) {
        event.preventDefault();
    	  var userSignInValues = {}; // dictionary of email and password entered by user
        let loginOrEmail = null;
        let password = null;

        if (!login) {
    	     loginOrEmail = document.getElementById("signInLoginOrEmail").value;
    	     password = document.getElementById("signInPassword").value;
        }
        else {
    	     loginOrEmail = login;
    	     password = passw;
        }

    	  if (loginOrEmail.length > 0 && password.length > 0) {
            let hashed_sha256 = CryptoJS.SHA256(password);
            let client_hashed = hashed_sha256.toString(CryptoJS.enc.Base64);
            userSignInValues.login_or_email = loginOrEmail;
            userSignInValues.password = client_hashed;
            sakura.apis.hub.login(userSignInValues).then(function (wsResult) {
    		    	  $('#signInModal').on('hidden.bs.modal', function () {
    	    			    $(this).find('form').trigger('reset');
                });
    	    		  $("#signInModal").modal("hide");

                fill_profil_button();
    	    		  current_login = wsResult;

                //Back to the current div
                var url = window.location.href.split('#');
                if (url.length > 1)
                    showDiv(event, url[1], '');
                else
                    showDiv(event, '', '');
    	    		  return;
            }).catch(
  	        function (error_message) {
  	    	      alert(error_message);
                if (DEBUG) console.log("E4", error_message);
            });
        } // end checking empty fields
        else {
            alert("Fill both the fields");
        }
    } //end if event click
}

function openUserProfil(event) {
    sakura.apis.hub.users.current.info().then(function (info) {
        fill_profil_modal(info);
    });
}

function logOut(event) {
    res = confirm("Sign Out?");
    if (res) {
      sakura.apis.hub.logout().then(function (result) {
            fill_profil_button();
            current_login = null;
        });
    }
}

function pwdRecoverySubmitControl(event) {
	if (event.type === 'click') {
	  event.preventDefault();
	  var pwdRecoveryValues = {}; // dictionary of email and password entered by user
	  let loginOrEmail = document.getElementById("pwdRecoveryLoginOrEmail").value;
	  if (loginOrEmail.length > 0){
		  pwdRecoveryValues.login_or_email = loginOrEmail;
	      sakura.apis.hub.recover_password(pwdRecoveryValues).then(
	        function (wsResult) {
                alert("Mail sent. Checkout your mailbox.");
                $('#signInModal').on('hidden.bs.modal', function () {
                      $(this).find('form').trigger('reset');
                });
                return;
            }).catch(
	        function (error_message) {
                  alert(error_message);
                  if (DEBUG) console.log("E5", error_message);
            });
      }
	  else {
		  alert("Fill the field");}}
}

function changePasswordSubmitControl(event) {
  	if (event.type === 'click') {
    	  event.preventDefault();
    	  var changePasswordValues = {}; // dictionary of email and password entered by user
    	  let loginOrEmail = document.getElementById("changePasswordLoginOrEmail").value;
    	  let currentPasswordOrRT = document.getElementById("changePasswordCurrentPasswordOrRT").value;
    	  let newPassword = document.getElementById("changePasswordNewPassword").value;
    	  let confirmPassword = document.getElementById("changePasswordConfirmPassword").value;
    	  if (newPassword != confirmPassword) {
            alert("New password and Confirm password should be the same.");
            return;
        }
    	  if ((loginOrEmail.length > 0) && (currentPasswordOrRT.length > 0) && (newPassword.length > 0)) {
            changePasswordValues.login_or_email = loginOrEmail;
            if (currentPasswordOrRT.substring(0, 4) == "rec-") {
                // recovery token, send it unmodified
                changePasswordValues.current_password_or_rec_token = currentPasswordOrRT
            }
            else {
                // current password, hash it
                let hashed_current_sha256 = CryptoJS.SHA256(currentPasswordOrRT);
                let client_current_hashed = hashed_current_sha256.toString(CryptoJS.enc.Base64);
                changePasswordValues.current_password_or_rec_token = client_current_hashed;
            }
            let hashed_new_sha256 = CryptoJS.SHA256(newPassword);
            let client_new_hashed = hashed_new_sha256.toString(CryptoJS.enc.Base64);
            changePasswordValues.new_password = client_new_hashed;
            sakura.apis.hub.change_password(changePasswordValues).then(function (wsResult) {
                console.log("wsResult:"+wsResult);
                alert("Password changed");
                $('#signInModal').on('hidden.bs.modal', function () {
                  $(this).find('form').trigger('reset');});
                $("#signInModal").modal("hide");
                return;
            }).catch(
    	      function (error_message) {
    	         alert(error_message);
               if (DEBUG) console.log("E6", error_message);
            });
        }
        else {
  	       alert("Fill all the fields");
        }
    }
}

function fill_profil_button() {
    sakura.apis.hub.users.current.info().then( function (login) {
        var gul = null;
        if (login) {
            var butt = $('<button>', {'class': "btn btn-secondary dropdown-toggle",
                                      'type': "button",
                                      'data-toggle':"dropdown",
                                      'id': "dropdownProfilButton"});
            var span = $('<span>', {'class': "glyphicon glyphicon-user",
                                    'aria-hidden': "true"})
            butt.append(span);
            butt.append('&nbsp;&nbsp;'+login.login+'&nbsp;&nbsp;');
            butt.append('<span class="caret"></span>');

            gul = $('<ul>', { 'class':"dropdown-menu dropdown-menu-right",
                                    'aria-labelledby': "dropdownProfilButton"});
            var li1 = $('<li>', {'role': "presentation"});
            var li2 = $('<li>', {'role': "presentation", 'class': "divider"});
            var li3 = $('<li>', {'role': "presentation"});

            var a1 = $('<a>', {     'class': "dropdown-item",
                                    'text': "Profil",
                                    'onclick': "openUserProfil(event);"});
            var a2 = $('<a>', {     'class': "dropdown-item",
                                    'href':"#",
                                    'text': "Log Out",
                                    'onclick': "logOut(event);"});
            li1.append(a1);
            li3.append(a2);
            gul.append(li1, li2, li3);

            current_login = login;

        }
        else {
            var butt = $('<button>', {'onclick': "initiateSignInModal(event);",
                                      'class': "btn btn-info",
                                      'data-toggle': "modal",
                                      'href': "#signInModal"});
            var span = $('<span>', {'class': "glyphicon glyphicon-user",
                                    'aria-hidden': "true"})
            butt.append(span);
            butt.append('&nbsp;&nbsp;Sign In');
            current_login = null;
        }
        $('#idSignInWidget').empty();
        $('#idSignInWidget').append(butt);
        if (gul) {
            $('#idSignInWidget').append(gul);
        }
    });
}

function fill_profil_modal(user_infos) {
    var keys = Object.keys(user_infos);

    var bdy = $('#profil_body');
    bdy.empty();

    var div = $('<div>', {  'class': "panel panel-default"});
    var divh = $('<div>', { 'class': "panel-heading",
                            'text': "General Informations"})
    var divb = $('<div>', { 'class': "panel-body"})

    var dl = $('<dl>', {'class': "dl-horizontal col-md-6",
                        'style': "margin-bottom: 0px; width: 100%;"})
    keys.forEach( function(key) {
        var dt = $('<dt>', {'text': key});
        var txt = user_infos[key];
        if (user_infos[key] === '' || user_infos[key] == null) {
            txt = '<i><font color="lightgrey">not specified</font></i>';
        }
        var dd = $('<dd>', {'html': txt});
        dl.append(dt, dd);
    });
    divb.append(dl);
    div.append(divh, divb);
    bdy.append(div);

    $('#profil_modal').modal('show');
}

function not_implemented(s = '') {
  if (s == '') {
    alert('Not implemented yet');
  } else {
    alert('Not implemented yet: ' + s);}
}

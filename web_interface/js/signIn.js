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
            sakura.common.ws_request('new_user', [], userAccountValues,
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
                },
                function (error_message) {
            	      alert(error_message);
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
            sakura.common.ws_request('login', [], userSignInValues, function (wsResult) {
    		    	  // console.log("wsResult:"+wsResult);
    		    	  $('#signInModal').on('hidden.bs.modal', function () {
    	    			    $(this).find('form').trigger('reset');
                });
    	    		  $("#signInModal").modal("hide");

                signInWidget = document.getElementsByName("signInWidget")[0];
    	    		  signInWidget.innerHTML = '<a onclick="signOutSubmitControl(event);" style="cursor: pointer;"><span class="glyphicon glyphicon-user" aria-hidden="true"></span>&nbsp;&nbsp;'+wsResult+'&nbsp;&nbsp;</a>';
    	    		  current_login = wsResult;

                //Back to the current div
                var url = window.location.href.split('#');
                showDiv(event, url[1], '');
    	    		  return;
            },
  	        function (error_message) {
  	    	      alert(error_message);
            });
        } // end checking empty fields
        else {
            alert("Fill both the fields");
        }
    } //end if event click
}

function signOutSubmitControl(event) {
    res = confirm("Sign Out?");
    if (res) {
      sakura.common.ws_request('logout', [], {}, function (result) {
            signInWidget = document.getElementsByName("signInWidget")[0];
            signInWidget.innerHTML = '<a class="btn" data-toggle="modal" data-target="#signInModal"><span class="glyphicon glyphicon-user" aria-hidden="true"></span> Sign in</a>';
            showDiv(event, "");
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
	      sakura.common.ws_request('recover_password', [], pwdRecoveryValues,
	        function (wsResult) {
                alert("Mail sent. Checkout your mailbox.");
                $('#signInModal').on('hidden.bs.modal', function () {
                      $(this).find('form').trigger('reset');
                });
                return;
            },
	        function (error_message) {
                  alert(error_message);
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
            sakura.common.ws_request('change_password', [], changePasswordValues, function (wsResult) {
                console.log("wsResult:"+wsResult);
                alert("Password changed");
                $('#signInModal').on('hidden.bs.modal', function () {
                  $(this).find('form').trigger('reset');});
                $("#signInModal").modal("hide");
                return;
            },
    	      function (error_message) {
    	         alert(error_message);
            });
        }
        else {
  	       alert("Fill all the fields");
        }
    }
}

function not_implemented(s = '') {
  if (s == '') {
    alert('Not implemented yet');
  } else {
    alert('Not implemented yet: ' + s);}
}

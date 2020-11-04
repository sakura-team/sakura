//date: September 2017
//author: rms-dev
//
//
//BEGIN: Refreshing the modal in case any parsley class attributes remain while user logins

var current_user = null;
var users_list = null;


function initiateSignInModal(event) {
    let $signUpForm = document.getElementById("signUpForm");
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
        let $selectCountry = $("#signUpCountry");
        let countryNames = [];
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
        let userAccountValues = {}; // dictionary of all values input by user
        let $modalForm = document.getElementById("signInModal");
        let formInstance = $('#signUpForm').parsley();

        formInstance.on('form:validated', function () {
            console.log("In form:validated function");
            ok = $('.parsley-error').length === 0;
            $('.bs-callout-info').toggleClass('hidden', !ok);
            $('.bs-callout-warning').toggleClass('hidden', ok);
        });

        let formValidated = formInstance.validate();
        if (formValidated) {
            let fieldsObj = formInstance.fields;
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

            //begin request calls for websocket
            push_request('users_create');
            sakura.apis.hub.users.create(userAccountValues).then(
              function (wsResult) {
                    pop_request('users_create');
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
            	      pop_request('users_create');
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
    	  let userSignInValues = {}; // dictionary of email and password entered by user
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
            push_request('login');
            sakura.apis.hub.login(userSignInValues).then(function (wsResult) {
                pop_request('login');
    		    	  $('#signInModal').on('hidden.bs.modal', function () {
    	    			    $(this).find('form').trigger('reset');
                });
    	    		  $("#signInModal").modal("hide");

                if (wsResult.privileges == null)
                    wsResult.privileges = { 'admin':     'granted',
                                            'developer': 'granted'};

                current_user = wsResult;
                fill_profil_button();

                //Back to the current div
                let url = window.location.href.split('#');
                if (url.length > 1)
                    showDiv(event, url[1], '');
                else
                    showDiv(event, '', '');
    	    		  return;
            }).catch(
  	        function (error_message) {
                pop_request('login');
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
        fill_profil_modal(current_user);
}

function logOut(event) {
    yes_no_asking('Sign Out', 'Are you sure you want to sign out ?', function() {
        push_request('logout');
        sakura.apis.hub.logout().then(function (result) {
            pop_request('logout');
            current_user = null;
            fill_profil_button();

            //cleaning pages
            $("[id^='web_interface_projects_li_project_']").each(function(){
                let pname = 'project_'+web_interface_current_id;
                if (this.id.indexOf(pname) == -1)
                    this.remove();
            });
            showDiv(event, 'Home');
        });
    });
}

function pwdRecoverySubmitControl(event) {
	if (event.type === 'click') {
	  event.preventDefault();
	  let pwdRecoveryValues = {}; // dictionary of email and password entered by user
	  let loginOrEmail = document.getElementById("pwdRecoveryLoginOrEmail").value;
	  if (loginOrEmail.length > 0){
		  pwdRecoveryValues.login_or_email = loginOrEmail;
        push_request('recover_password');
	      sakura.apis.hub.recover_password(pwdRecoveryValues).then(
	        function (wsResult) {
                pop_request('recover_password');
                alert("Mail sent. Checkout your mailbox.");
                $('#signInModal').on('hidden.bs.modal', function () {
                      $(this).find('form').trigger('reset');
                });
                return;
            }).catch(
	        function (error_message) {
                  pop_request('recover_password');
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
    	  let changePasswordValues = {}; // dictionary of email and password entered by user
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
            push_request('change_password');
            sakura.apis.hub.change_password(changePasswordValues).then(function (wsResult) {
                pop_request('change_password');
                alert("Password changed");
                $('#signInModal').on('hidden.bs.modal', function () {
                  $(this).find('form').trigger('reset');});
                $("#signInModal").modal("hide");
                return;
            }).catch(
    	      function (error_message) {
                pop_request('change_password');
    	          alert(error_message);
                if (DEBUG) console.log("E6", error_message);
            });
        }
        else {
  	       alert("Fill all the fields");
        }
    }
}

function fill_profil_button(fill_modal) {
    push_request('users_current');
    sakura.apis.hub.users.current.info().then( function (result) {
        pop_request('users_current');
        if (result) {
            current_user = result;

            function fill(login, pends) {
                let gul = null;
                let butt = $('<button>', {'class': "btn btn-info dropdown-toggle btn-xs",
                                          'type': "button",
                                          'data-toggle':"dropdown",
                                          'id': "dropdownProfilButton"});
                let span = $('<span>', {'class': "glyphicon glyphicon-user",
                                        'aria-hidden': "true"})
                butt.append(span);
                butt.append('&nbsp;&nbsp;'+login.login+'&nbsp;&nbsp;');
                butt.append('<span class="caret"></span>');

                gul = $('<ul>', { 'class':"dropdown-menu dropdown-menu-right",
                                        'aria-labelledby': "dropdownProfilButton"});
                let li1 = $('<li>', {'role': "presentation"});
                let li2 = $('<li>', {'role': "presentation", 'class': "divider"});
                let li3 = $('<li>', {'role': "presentation"});

                let ex_span = $('<span>', { 'class': "glyphicon glyphicon-exclamation-sign",
                                            'aria-hidden': "true",
                                            'style': 'color: orange; position: absolute; left:3px; top: 0px; display: block;'});
                let a1 = $('<a>', {     'class': "dropdown-item",
                                        'html': "Profile",
                                        'onclick': "openUserProfil(event);",
                                        'style': "cursor: pointer;"});
                if (pends)
                      a1.append(ex_span);

                let a2 = $('<a>', {     'class': "dropdown-item",
                                        'html': "Log Out&nbsp;&nbsp;",
                                        'onclick': "logOut(event);"});
                let span_off = $('<span>', {'class': "glyphicon glyphicon-off",
                                            'aria-hidden': "true"});
                a2.append(span_off);
                li1.append(a1);
                li3.append(a2);
                gul.append(li1, li2, li3);

                if (pends)
                    $('#profile_button_exclamation').css('display', 'block');
                else
                    $('#profile_button_exclamation').css('display', 'none');

                $('#idSignInWidget').empty();
                $('#idSignInWidget').append(butt);
                if (gul) {
                    $('#idSignInWidget').append(gul);
                }
            }

            if (current_user.privileges.indexOf('admin') != -1) {
                push_request('users_list');
                sakura.apis.hub.users.list().then(function (result){
                    pop_request('users_list');
                    users_list = result;
                    let pendings = users_list.some( function(user){
                              return user.requested_privileges.length !== 0;
                            });
                    fill(current_user, pendings);
                    if (fill_modal)
                        fill_profil_modal(current_user);
                });
            }
            else {
                fill(current_user, null);
                if (fill_modal)
                    fill_profil_modal(current_user);
            }

        }
        else {
            let butt = $('<button>', {'onclick': "initiateSignInModal(event);",
                                      'class': "btn btn-info btn-xs",
                                      'data-toggle': "modal",
                                      'href': "#signInModal"});
            let span = $('<span>', {'class': "glyphicon glyphicon-user",
                                    'aria-hidden': "true"})
            butt.append(span);
            butt.append('&nbsp;&nbsp;Sign In');
            $('#profile_button_exclamation').css('display', 'none');
            $('#idSignInWidget').empty();
            $('#idSignInWidget').append(butt);
            current_user = null;
        }
    });
}

function fill_profil_modal(user_infos) {
    let bdy = $('#profil_body');
    bdy.empty();

    let div   = $('<div>', {  'class': "panel panel-default"});
    let divh  = $('<div>', {  'class': "panel-heading",
                              'html':  "<h4 style=\"margin-bottom: 0px; \
                                        margin-top: 0px\">General Informations</h4>",
                              'style': "margin-bottom: 0px; margin-top: 0px"})
    let divb  = $('<div>', {  'class': "panel-body"})
    let dl    = $('<dl>', {   'class': "dl-horizontal col-md-6",
                              'style': "margin-bottom: 0px; width: 100%;"})

    Object.keys(user_infos).forEach( function(item) {
        if (item != 'privileges' && item != 'requested_privileges') {
            let txt = user_infos[item];
            if (user_infos[item] === '' || user_infos[item] == null) {
                txt = '<i><font color="lightgrey">not specified</font></i>';
            }
            if (item == 'login') {
                txt = '<b>'+txt+'</b>';
            }
            else {
                txt = $('<a name="short_desc" href="#" data-type="text" data-title="txt">'+txt+'</a>');
                txt.editable({emptytext: txt,
                            url: function(params) {update_profile(item, txt, params);}});
            }
            dl.append($('<dt>', {'text': item}),
                      $('<dd>', {'html': txt}));
        }
    });
    bdy.append(div.append(divh, divb.append(dl)));

    div = $('<div>', {  'class': "panel panel-default"});
    divh = $('<div>', { 'class': "panel-heading",
                            'html': "<h4 style=\"margin-bottom: 0px; \
                                    margin-top: 0px\">Your Privileges</h4>"})
    divb = $('<div>', { 'class': "panel-body"})

    dl = $('<dl>', {'class': "dl-horizontal col-md-6",
                        'style': "margin-bottom: 0px; width: 100%;"})

    let priv_dict = { 'granted':      'btn btn-success btn-xs',
                      'not granted':  'btn btn-secondary btn-xs',
                      'pending':      'btn btn-warning btn-xs'};

    let possible_privileges = ['admin', 'developer'];
    let found_privileges = [];

    possible_privileges.forEach( function(privilege) {
        let dd = $('<dd>');
        if (user_infos.privileges.indexOf(privilege) != -1){
            let a = $('<button>', { 'type': "button",
                                    'class': 'btn btn-success btn-xs',
                                    'style': "width: 150px;",
                                    'text': 'granted'});
            a.prop('disabled', true);
            dd.append(a);
        }
        else if (user_infos.requested_privileges.indexOf(privilege) != -1) {
            let a = $('<button>', { 'type': "button",
                                    'class': 'btn btn-warning btn-xs',
                                    'style': "width: 150px;",
                                    'text': 'pending'});
            a.prop('disabled', true);
            dd.append(a);
        }
        else {
          let a = $('<button>', { 'type': "button",
                                  'style': "cursor: pointer;",
                                  'class': "btn btn-primary btn-xs btn-block",
                                  'style': "width: 150px;",
                                  'text': "ask for"});
          a.attr('onclick', "ask_for_privilege_open_modal(\""+privilege+"\");");
          dd.append(a);
        }
        dl.append($('<dt>', {'text': privilege}), dd);
    });

    bdy.append(div.append(divh, divb.append(dl)));

    if (user_infos.privileges.indexOf('admin') != -1) {
        //TABLE HEAD
        let pdiv = $('<div>', {  'class': "panel panel-default",
                                'style': "margin-bottom: 0px;"});
        let pdivh = $('<div>', { 'class': "panel-heading",
                                'html': "<h4 style=\"margin-bottom: 0px; \
                                        margin-top: 0px\">User Privileges</h4>"})
        let pdivb = $('<div>', {  'class': "panel-body"})

        let ptable = $('<table>', { 'width': '100%',
                                    'class': "table table-striped table-condensed header-fixed",
                                    'style': "margin-bottom: 0px"});
        let pthead = $('<thead>', {'style': "background: lightgray;"});
        let ptbody = $('<tbody>');
        let th1 = $('<th>', { 'html': '<b>&nbsp;</b>',    'style': "text-align: center;"});
        let th2 = $('<th>', { 'html': '<b>admin</b>',     'style': "text-align: center;"});
        let th3 = $('<th>', { 'html': '<b>developer</b>', 'style': "text-align: center;"});
        let tr = $('<tr>');
        pthead.append(tr.append(th1, th2, th3));

        function new_check(user, privilege){
            let i = $('<input>', { 'type': "checkbox",});
            i.on('change', function (event) {
                update_privilege(event, user.login, privilege, event);
            });
            return i;
        }
        function y_button(user, privilege) {
            return $('<span>', {'class':"glyphicon glyphicon-ok",
                                'style':"color:green; cursor: pointer;",
                                'title': "accept privilege request",
                                'onclick': 'validate_pending(true, "'+user+'","'+privilege+'");'});
        }
        function n_button(user, privilege) {
            return $('<span>', {'class':"glyphicon glyphicon-remove",
                                'style':"color:red; cursor: pointer;",
                                'title': "refuse privilege request",
                                'onclick': 'validate_pending(false, "'+user+'","'+privilege+'");'});
        }

        users_list.forEach( function(user){
            let tr = $('<tr>');
            let td1 = $('<td>', { 'html': user.login,
                                  'align': "center",
                                  'style': "padding: 0px"
                                  });
            let td2 = $('<td>', { 'align': "center",
                                  'style': "padding: 0px"
                                  });
            let td3 = $('<td>', { 'align': "center",
                                  'style': "padding: 0px"
                                  });
            let tog1 = new_check(user, 'admin');
            if (user.privileges.indexOf('admin') != -1) {
                tog1.prop('checked', true);
            }
            else if (user.requested_privileges.indexOf('admin') != -1) {
                td2.attr('style', 'background: orange; padding: 0px;');
                tog1 = $('<div>');
                tog1.append(y_button(user.login, 'admin'), "&nbsp;&nbsp;", n_button(user.login, 'admin'));
            }

            let tog2 = new_check(user, 'developer');
            if (user.privileges.indexOf('developer') != -1) {
                tog2.prop('checked', true);
            }
            else if (user.requested_privileges.indexOf('developer') != -1) {
                td3.attr('style', 'background: orange; padding: 0px;');
                tog2 = $('<div>');
                tog2.append(y_button(user.login, 'developer'), "&nbsp;&nbsp;", n_button(user.login, 'developer'));
            }
            ptbody.append(tr.append(td1, td2.append(tog1), td3.append(tog2)));
        });
        ptable.append(pthead,ptbody);
        bdy.append(pdiv.append(pdivh, pdivb.append(ptable)));
    }
    $('#profil_modal').modal('show');
}

function validate_pending(value, login, privilege){
    let func_yes = function() {
        if (value == true) {
            push_request('users_privileges');
            sakura.apis.hub.users[login].privileges.add(privilege).then(function () {
                pop_request('users_privileges');
                fill_profil_button(true);
            });
        }
        else {
            push_request('users_privileges');
            sakura.apis.hub.users[login].privileges.deny(privilege).then(function () {
                pop_request('users_privileges');
                fill_profil_button(true);
            });
        }
    }
    if (!value) {
        yes_no_asking("Refusing Pending Privilege",
                      "Are you sure you want to refuse "+login+"'s <b>"+privilege+"</b> privilege ?",
                      func_yes);
    }
    else {
        yes_no_asking("Validating Pending Privilege",
                      "Are you sure you want to validate "+login+"'s <b>"+privilege+"</b> privilege ?",
                      func_yes);
    }
}

function update_privilege(event, login, privilege, checkbox) {
    let value = event.target.checked;
    let func_yes = function() {
        if (value) {
            push_request('users_privileges');
            sakura.apis.hub.users[login].privileges.add(privilege).then(function (result) {
                pop_request('users_privileges');
                fill_profil_button(true);
            });
        }
        else {
            push_request('users_privileges');
            sakura.apis.hub.users[login].privileges.remove(privilege).then(function (result) {
                pop_request('users_privileges');
                fill_profil_button(true);
            });
        }
    }
    let func_no = function() {
        event.target.checked = !event.target.checked;
    }

    if (!value) {
        yes_no_asking("Removing Privilege",
                      "Are you sure you want to remove "+login+"'s <b>"+privilege+"</b> privilege ?",
                      func_yes,
                      func_no);
    }
    else {
        yes_no_asking("Adding Privilege",
                      "Are you sure you want to add "+login+"'s <b>"+privilege+"</b> privilege ?",
                      func_yes,
                      func_no);
    }
}


function update_profile(item, a, params) {
    let kwargs = {};
    kwargs[item] = params.value;
    push_request('users_current');
    sakura.apis.hub.users.current.update(kwargs).then( function(result) {
        pop_request('users_current');
        if (result) {
            alert('something went wrong');
        }
    });
}

//Privilege Managment
function ask_for_privilege_open_modal(privilege) {

    let txt1 = "An email will be sent to the administrators for asking for \
                a <b>"+privilege+"</b> status. Please describe your needs.";

    let txt2 = "Hello,\n\nI am a ...,\n";
    txt2 += "I would like to get "+privilege+" status for ...\n\n";
    txt2 += "Thank you !";
    h = $('#web_interface_asking_privilege_modal_header');
    b = $('#web_interface_asking_privilege_modal_body');
    h.empty();
    b.empty();
    h.append("<h3><font color='white'>Asking for "+privilege+" Access</font></h3>");
    b.append($('<p>', {html: txt1}));

    let ti = $('<textarea>', {  class: 'form-control',
                                id: 'web_interface_asking_privilege_textarea',
                                rows: '6',
                                text: txt2});
    b.append(ti);
    $('#web_interface_asking_privilege_modal_button').click(function () { ask_for_privilege(privilege, null)});
    $('#web_interface_asking_privilege_modal').modal('show');
}

function ask_for_privilege(privilege, callback) {
    push_request('users_current_privileges');
    sakura.apis.hub.users.current.privileges.request(privilege).then( function(result) {
        pop_request('users_current_privileges');
        if (!result) {
            $('#web_interface_asking_privilege_modal').modal('hide');
            let header = 'Asking For New Status';
            let body = '<h4 align="center" style="margin: 5px;"><font color="black"> Email sent !!</font></h4>';
            main_success_alert(header, body, null, 1);
            fill_profil_button(true)
        }
        else {
            alert('something went wrong !');
        }
    });
}

function not_implemented(s = '') {
  if (s == '') {
    alert('Not implemented yet');
  } else {
    alert('Not implemented yet: ' + s);}
}

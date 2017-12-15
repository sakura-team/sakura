//date: September 2017
//author: rms-dev
//
//
//BEGIN: Refreshing the modal in case any parsley class attributes remain while user logins
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

  //END: Refreshing the modal

  // BEGIN: Populating the country codes -------------
  // RMS: Change the default country in this code block if required.
  // RMS: Update country-codes.json for correcting erroneous entries, if any.
  $.getJSON("./divs/signIn/country-codes.json", function (data) {
    var $selectCountry = $("#signUpCountry");
    var countryNames = [];
    // console.log(data);
    $selectCountry.empty();
    $.each(data, function (idx, entry) {
      if (entry.name === 'France') {
        $selectCountry.append("<option selected='selected'>" + entry.name + "</option>");
      } else {
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
      if (fieldsObj.length > 0)
      {
        fieldsObj.forEach(function (fieldIdx) {
          // console.log('fieldIdx ' + fieldIdx);
          // console.log(fieldIdx.element.name + "=" + fieldIdx.value);
          userAccountValues[fieldIdx.element.name] = fieldIdx.value;
        });
      } else {
        console.log("ERROR: Form fields are empty"); //checking for empty fields
      }
      delete userAccountValues['signUpConfirmPassword'];
      delete userAccountValues['signInCGU'];
      // console.log(userAccountValues); //before password hashing
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
	    	  // console.log("wsResult:"+wsResult);
	    	  if (wsResult) {
	    		  userAccountValues = {};
	    		  alert("'"+login + "' has been registered");
	    		  $('#signInModal').on('hidden.bs.modal', function () {
	    			  $(this).find('form').trigger('reset');
	    		  });
	    		  $("#signInModal").modal("hide");
	    		  return;
	    	  } else {
	    		  console.log("Error callbacks in the new_user function need to be handled properly");
	    		  return;
	    	  }
        }, 
        function (error_message) {
    	      alert(error_message);
    	  }); 
    } else {
      console.log("Form validation failed");
    }
  } // end if click
}

function signInSubmitControl(event) {
	if (event.type === 'click') {
	  event.preventDefault();
	  var userSignInValues = {}; // dictionary of email and password entered by user
	  let email = document.getElementById("signInEmail").value;
	  let password = document.getElementById("signInPassword").value;
	  if (email.length > 0 && password.length > 0){
		  let hashed_sha256 = CryptoJS.SHA256(password);
		  let client_hashed = hashed_sha256.toString(CryptoJS.enc.Base64);
		  userSignInValues['email'] = email;
		  userSignInValues['password'] = client_hashed
	      sakura.common.ws_request('login', [], userSignInValues, 
	        function (wsResult) {
		    	  // console.log("wsResult:"+wsResult);
		    	  alert("Login successful");
		    	  $('#signInModal').on('hidden.bs.modal', function () {
	    			  $(this).find('form').trigger('reset');
	    		  });
	    		  $("#signInModal").modal("hide");
	    		  firstSignInWidget = document.getElementsByName("twinSignInWidgets")[0];
	    		  secondSignInWidget = document.getElementsByName("twinSignInWidgets")[1];
	    		  firstSignInWidget.innerHTML = '<a onclick="signOutSubmitControl(event);" href="http://sakura.imag.fr/signOut" style="cursor: pointer;"><span class="glyphicon glyphicon-user" aria-hidden="true"></span>'+wsResult+'</a>';
	    		  secondSignInWidget.innerHTML = '<a onclick="signOutSubmitControl(event);" href="http://sakura.imag.fr/signOut" style="cursor: pointer;"><span class="glyphicon glyphicon-user" aria-hidden="true"></span>'+wsResult+'</a>';    		  
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
	  firstSignInWidget = document.getElementsByName("twinSignInWidgets")[0];
		secondSignInWidget = document.getElementsByName("twinSignInWidgets")[1];
	    firstSignInWidget.innerHTML = '<a class="btn" data-toggle="modal" data-target="#signInModal"><span class="glyphicon glyphicon-user" aria-hidden="true"></span> Sign in</a>';
	    secondSignInWidget.innerHTML = '<a class="btn" data-toggle="modal" data-target="#signInModal"><span class="glyphicon glyphicon-user" aria-hidden="true"></span> Sign in</a>';
    showDiv(event, "");
    return;
  } else {
    showDiv(event, 'HelloYou');
  }
}

function not_implemented(s = '') {
  if (s == '') {
    alert('Not implemented yet');
  } else {
    alert('Not implemented yet: ' + s);
}
}

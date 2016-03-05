//***************** ALL BACK BUTTONS ******************//
function separate_comma(ip_str){
	var ret_str = ip_str.split('').reverse().join('');
	ret_str = ret_str.replace(/(.{3})/g,",$1").split('').reverse().join('');
	ret_str = ret_str.replace(/,$/, "");
	return ret_str;
}


//****************** LOGIN PAGE ***********************//
jQuery(document).ready(function($) {
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "https://api.levelmoney.com/api/v2/hackathon/login", true);
	xhr.setRequestHeader('Content-Type', 'application/json');
	xhr.setRequestHeader('Accept', 'application/json');
	xhr.onloadend = function() {
	    var parsed = JSON.parse(this.response);
	    var pretty = JSON.stringify(parsed, null, 2);
	};
	xhr.onerror = function(err) {
	    // document.getElementById('login_caption').textContent = "ugh an error. i can't handle this right now.";
	};
	args = {"email": "hackdoc@levelmoney.com", "password": "hackathon1"};
	xhr.send(JSON.stringify(args));
	// alert("1234567890".replace(/(.{3})/g,",$1"));


	var xhr = new XMLHttpRequest();
	xhr.open("POST", "https://api.levelmoney.com/api/v2/hackathon/get-accounts", true);
	xhr.setRequestHeader('Content-Type', 'application/json');
	xhr.setRequestHeader('Accept', 'application/json');
	xhr.onloadend = function() {
		var accounts = JSON.parse(this.response)['accounts'];
		var total_balance = 0;
		$('#fin_overview_accounts').empty();
		for(i=0; i < accounts.length; i++){
			var balance = parseFloat(accounts[i]['balance'])/1000;
			balance_str = separate_comma(balance.toString());			
			total_balance += balance;
			$('<div>\
				<h2>Checking &amp; Savings</h2>\
				<div class="acct-left">\
	            <p><strong>Checking Account</strong><br/>\
	            xxxx-xxxx-xxxx-'+accounts[i]['last-digits'] +'</p>\
		          </div>\
		          <div class="acct-right">$'+ balance_str + '</div><div class="clear" style="clear: both;"></div>\
		          <div class="savings-total"><h3>Total Saved: $'+ balance_str + '</h3></div>'
	        	).appendTo('#fin_overview_accounts');
		}
		// document.getElementById('fin_overview_total_balance').textContent = "Total Balance: $" + separate_comma(total_balance.toString());
	};
	xhr.onerror = function(err) {
	    // document.getElementById('accounts_list').textContent = "ugh an error. i can't handle this right now.";
	};
	args = {"args": {"uid":  1110568334, "token":  "209E16DD45691753346973B767432F93", "api-token":  "HackathonApiToken"}};
	xhr.send(JSON.stringify(args));
});

//****************** YET TO BE USED ***********************//
$("#get_transactions").click(function()
{
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "https://api.levelmoney.com/api/v2/hackathon/get-all-transactions", true);
	xhr.setRequestHeader('Content-Type', 'application/json');
	xhr.setRequestHeader('Accept', 'application/json');
	xhr.onloadend = function() {
	    var parsed = JSON.parse(this.response);
	    var pretty = JSON.stringify(parsed, null, 2);
	    $.getJSON('/_transactions', {
        transaction_list: pretty
      	}, function(data) {
        // $("#result").text(data.result);
      	});
	    document.getElementById('trans_list').textContent = pretty;
	};
	xhr.onerror = function(err) {
	    document.getElementById('trans_list').textContent = "ugh an error. i can't handle this right now.";
	};
	args = {"args": {"uid":  1110568334, "token":  "209E16DD45691753346973B767432F93", "api-token":  "HackathonApiToken"}};
	xhr.send(JSON.stringify(args));
});

$("#get_projected_transactions").click(function()
{
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "https://api.levelmoney.com/api/v2/hackathon/projected-transactions-for-month", true);
	xhr.setRequestHeader('Content-Type', 'application/json');
	xhr.setRequestHeader('Accept', 'application/json');
	xhr.onloadend = function() {
	    var parsed = JSON.parse(this.response);
	    var pretty = JSON.stringify(parsed, null, 2);
	    $.getJSON('/_projected_transactions', {
        proj_transaction_list: pretty
      	}, function(data) {
        // $("#result").text(data.result);
      	});
	    document.getElementById('projected_trans').textContent = pretty;
	};
	xhr.onerror = function(err) {
	    document.getElementById('projected_trans').textContent = "ugh an error. i can't handle this right now.";
	};
	args = {"args": {"uid":  1110568334, "token":  "209E16DD45691753346973B767432F93", "api-token":  "HackathonApiToken"}, "year":  2015, "month":  3};
	xhr.send(JSON.stringify(args));
});

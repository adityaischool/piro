//***************** ALL BACK BUTTONS ******************//
function separate_comma(ip_str){
	return ip_str;
	var dot_index = ip_str.indexOf('.');
	if(dot_index > 0){
		var new_str = ip_str.substring(0,dot_index);
		var ret_str = new_str.split('').reverse().join('');
		ret_str = ret_str.replace(/(.{3})/g,",$1").split('').reverse().join('');
		ret_str = ret_str.replace(/,$/, "");
		console.log(ret_str);
		ret_str += ip_str.substring(dot_index,ip_str.length);
	}
	
	console.log(ret_str)
	ret_str = ret_str.replace('.,','.');
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
	xhr.open("POST", "https://api.levelmoney.com/api/v2/hackathon/get-all-transactions", true);
	xhr.setRequestHeader('Content-Type', 'application/json');
	xhr.setRequestHeader('Accept', 'application/json');
	xhr.onloadend = function() {
	    var resp = JSON.parse(this.response)['transactions'];
	    var transactions = [];
	    resp.forEach(function(obj) {
	     	if(obj['amount'] < 0)
	     		transactions.push(obj);
	 	});
	    catname_list = ['Food and Drinks', 'Travel', 'Electronics', 'Clothes and Shoes'];
	    cat_len = parseInt(transactions.length*0.25);
	    cat_exp = 0;
	    console.log('cat_len:' + cat_len, transactions.slice(0,cat_len).length);
	    $.each(transactions.slice(0,cat_len), function(i, data) {
            cat_exp += data['amount'];
        });
        cat_exp = -cat_exp/1000;
        $('<div>\
				<p>'+catname_list[0]+': $' + separate_comma(cat_exp.toString()) +'</p>\
	  		</div>').appendTo('#categ_exps');

        cat_exp = 0;
	    $.each(transactions.slice(cat_len, cat_len*2), function(i, data) {
	    	cat_exp += data['amount'];
        });
        cat_exp = -cat_exp/1000;
        $('<div>\
				<p>'+catname_list[1]+': $' + separate_comma(cat_exp.toString()) +'</p>\
	  		</div>').appendTo('#categ_exps');

        cat_exp = 0;
	    $.each(transactions.slice(cat_len*2, cat_len*3), function(i, data) {
            cat_exp += data['amount'];
        });
        cat_exp = -cat_exp/1000;
        $('<div>\
				<p>'+catname_list[2]+': $' + separate_comma(cat_exp.toString()) +'</p>\
	  		</div>').appendTo('#categ_exps');

        cat_exp = 0;
	    $.each(transactions.slice(cat_len*3, transactions.length), function(i, data) {
            cat_exp += data['amount'];
        });
        cat_exp = -cat_exp/1000;
        $('<div>\
				<p>'+catname_list[3]+': $' + separate_comma(cat_exp.toString()) +'</p>\
	  		</div>').appendTo('#categ_exps');
	};
	xhr.onerror = function(err) {
	    // document.getElementById('trans_list').textContent = "ugh an error. i can't handle this right now.";
	};
	args = {"args": {"uid":  1110568334, "token":  "209E16DD45691753346973B767432F93", "api-token":  "HackathonApiToken"}};
	xhr.send(JSON.stringify(args));
});

//****************** YET TO BE USED ***********************//
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

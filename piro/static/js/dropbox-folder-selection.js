// CODE FOR THE DROPBOX PHOTO FOLDER SELECTION PAGE 


// Bind click handler to submit selected folders button
$("#submit-dropbox-folders").on('click', function submitCheckedBoxes() {
	processCheckboxes($("input[type=checkbox]"));
});

// Handler for when user confirms selected folders
function processCheckboxes(checkboxes) {
	var folders = {'data': []};
	checkboxes.each(function() {
		var checkbox = $(this);
		tempFolder = {};
		tempFolder['path'] = checkbox.attr('data-value');
		if (checkbox.is(':checked')) {
			tempFolder['checked'] = 'checked';
		} else {
			tempFolder['checked'] = 'unchecked';
		}
		folders['data'].push(tempFolder);
	})
	var stringifiedPaths = JSON.stringify(folders);
	// Send folder paths & sync selection back to server
	$.get('/dropbox-user-selected-folders',
		{paths: stringifiedPaths});
}

// Check which folders, if any, a user has already selected to sync, then auto-check
// those folders or use the provided keyword list in markPhotoFoldersAsChecked
function getUserFolderSelections() {
	$.get('/get-dropbox-user-selected-folders',
		function(response) {
			console.log(response);
			markPhotoFoldersAsChecked(response);
	});
}

// Automatically check folders using user's selected folders OR keywords 'photo', 'pic', 'camera', or 'gallery'
function markPhotoFoldersAsChecked(userFolderSelections) {
	var photoFolderKeywordList = [
	'photo',
	'pic',
	'camera',
	'gallery'
	]
	// Select all of the checkbox elements
	var checkboxes = $(".dropbox-folder-item-checkbox");
	if (userFolderSelections['folders'].length > 0) {
		for (var i=0; i<checkboxes.length; i++) {
			for (var i2=0; i2<userFolderSelections['folders'].length; i2++) {
				var checkboxValue = checkboxes[i].value.toLowerCase();
				if (checkboxValue.indexOf(userFolderSelections['folders'][i2].split('/')[1]) > -1) {
					checkboxes[i].setAttribute("checked", "checked");
				}
			}
		}
	} else {
		for (var i=0; i<checkboxes.length; i++) {
			var checkboxValue = checkboxes[i].value.toLowerCase();
			for (var i2=0; i2<photoFolderKeywordList.length; i2++) {
				if (checkboxValue.indexOf(photoFolderKeywordList[i2]) > -1) {
					checkboxes[i].setAttribute("checked", "checked");
				}
			}
		}
	}
}

$(document).ready(getUserFolderSelections);
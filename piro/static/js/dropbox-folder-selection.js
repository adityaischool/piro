// CODE FOR THE DROPBOX PHOTO FOLDER SELECTION PAGE 


// Bind click handler to submit selected folders button
$("#submit-dropbox-folders").on('click', function submitCheckedBoxes() {
	processCheckboxes($("input[type=checkbox]"));
});

// Handler for when user confirms selected folders
// Sends selected folder paths back to web server to be stored in web server db
function processCheckboxes(checkboxes) {
	var folders = {'data': []};
	checkboxes.each(function() {
		var checkbox = $(this);
		console.log(checkbox.attr('data-value'), checkbox.is(':checked'));
		tempFolder = {};
		tempFolder['path'] = checkbox.attr('data-value');
		if (checkbox.is(':checked')) {
			tempFolder['checked'] = 'checked';
		} else {
			tempFolder['checked'] = 'unchecked';
		}
		folders['data'].push(tempFolder);
	})

	console.log(folders);
	var stringifiedPaths = JSON.stringify(folders);

	$.get('/dropbox-user-selected-folders',
		{paths: stringifiedPaths});
}

// Automatically check folders with keywords 'photo', 'pic', 'camera', or 'gallery'
function markPhotoFoldersAsChecked() {
	var photoFolderKeywordList = [
	'photo',
	'pic',
	'camera',
	'gallery'
	]
	var checkboxes = $(".dropbox-folder-item-checkbox");
	for (var i=0; i<checkboxes.length; i++) {
		var checkboxValue = checkboxes[i].value.toLowerCase();
		for (var i2=0; i2<photoFolderKeywordList.length; i2++) {
			if (checkboxValue.indexOf(photoFolderKeywordList[i2]) > -1) {
				checkboxes[i].setAttribute("checked", "checked");
			}
		}
	}
}

$(document).ready(markPhotoFoldersAsChecked);
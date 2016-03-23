/// 

$("#submit-dropbox-folders").on('click', function submitCheckedBoxes() {
	processCheckboxes($("input[type=checkbox]:checked"));
});

function processCheckboxes(checkboxes) {
	var folderPaths = [];
	for (var i=0; i<checkboxes.length; i++) {
		folderPaths.push(checkboxes[i].getAttribute('data-value'));
	}

	var stringifiedPaths = JSON.stringify(folderPaths);

	$.get('/dropbox-user-selected-folders',
		{paths: stringifiedPaths});
}
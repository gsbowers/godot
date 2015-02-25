window.onload=onload;

function onload(){

	//set start/end date of campaign1; add 12 hours to avoid tz issues 
	window.startDate = new Date("2014-12-04");
	startDate.setHours(startDate.getHours()+12);
	window.endDate = new Date("2015-02-09");
	endDate.setHours(endDate.getHours()+12);

	//check URL for date
	//initialize current date
	var URLDate = getURLDate();
	if (URLDate != null)
		window.curDate = URLDate;
	else 
		//window.curDate = new Date("2014-12-04");
		window.curDate = startDate;

	//https://gist.github.com/foxxtrot/309806
	YUI.namespace('godotNamespace');

	YUI().use('calendar', 'datatype-date', 'cssbutton',  function(Y) {

    // Create a new instance of calendar, placing it in
    // #mycalendar container, setting its width to 340px,
    // set the date startDate
    var calendar = new Y.Calendar({
      contentBox: "#calendar",
      width:'300px',
      showPrevMonth: true,
      showNextMonth: true,
			maximumDate: new Date(2016, 1, 1),
      date: curDate,
		}).render();

		//primary call to renderplots happens in here 
		//where calender selection change occurs
    calendar.on("selectionChange", function (ev) {
			var newDate = ev.newSelection[0];	
			if(typeof newDate !== 'undefined')
				curDate = newDate;
			renderplots();
    });

		//YUI3 bug: add 12hours to date before selecting it
		var selectDate = new Date(curDate);
		selectDate.setHours(selectDate.getHours()+12);
		calendar.selectDates(selectDate);

		YUI.godotNamespace.updateDate = function(d){
			calendar.set("date", d);
			calendar.deselectDates();
			calendar.selectDates(d);
		};

	});
}


function getURLParameter(name){
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function getURLDate(){
	var URLDate = getURLParameter("date");
	if (URLDate != ''){
		var arrDate = [URLDate.substr(0,4), URLDate.substr(4,2), URLDate.substr(6,2)];
		return new Date(arrDate.join('-'));
	} else {
		return null;
	}
}

function processCheckClick(){

	if(!document.getElementById("check_lgbin").checked)
		document.getElementById("lgbin").style.display="none";
	else
		document.getElementById("lgbin").style.display="inline";

	if(!document.getElementById("check_smbin").checked)
		document.getElementById("smbin").style.display="none";
	else
		document.getElementById("smbin").style.display="inline";
}

function AddZero(num){
	return (num >= 0 && num < 10) ? "0" + num : num + "";
}

function incrementDate(i){
	curDate.setDate(curDate.getDate() + i);
	YUI.godotNamespace.updateDate(curDate);
}

function renderplots(){

	var strDate = getDateStr(curDate);
	document.getElementById("plot_lgbin").src = "../quicklook/lgbin/godot_"+strDate+".png";
	document.getElementById("plot_smbin").src = "../quicklook/smbin/_godot_"+strDate+".png";
}

function getDateStr(d){
	var strDate = [AddZero(d.getFullYear()-2000), AddZero(d.getMonth()+1), AddZero(d.getDate())].join("");
	return strDate;
}

function getFullDateStr(d){
	var strDate = [AddZero(d.getFullYear()), AddZero(d.getMonth()+1), AddZero(d.getDate())].join("");
	return strDate;
}

function directURL(){
	var URL = "http://godot.jp/browser/?date="+getFullDateStr(curDate);
	document.getElementById("directURL").href=URL;
}

function resetDate(){
	curDate = startDate;
	YUI.godotNamespace.updateDate(curDate);
}

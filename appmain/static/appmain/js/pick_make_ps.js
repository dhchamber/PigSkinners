var bClosed;
var bPicksChanged = false;
var bAllowPicks = true;

function window_onload() {
	var sMsg;

	//see if there's a message to show the user
    bAllowPicks = true;
	sMsg = "Welcome to the Playoffs!";      //"<%=sOnOpenMsg%>";
//	if(sMsg != "") {
//		alert(sMsg);
//	}
}

function window_onbeforeunload() {
	if(bPicksChanged == true) {
		event.returnValue = "You have unsaved picks.\nNavigating away from the page will cause those picks to be lost.";
    }
}

$('form#frmPostPicks').submit(function() {
   $(window).unbind('beforeunload');
});

function pickTeam(objTd)
{
	var allowPicks = "True";
	var id = objTd.id;
	if(allowPicks == "True"){
		bPicksChanged = true;
		if(id == "htAWC36"){
			//if the 3 seed is picked then it plays the 2 seed in DIV (vtADIV2)
			vtADIV2.innerHTML = objTd.innerHTML;
			vtADIV2.setAttribute("teamID", htAWC36.getAttribute("teamID"));
            frmPostPicks.id_AWC36.value =  htAWC36.getAttribute("teamID");
            frmPostPicks.id_AvtDiv2.value = htAWC36.getAttribute("teamID");

			//if they changed the winner of this game, we need to clear out the afc picks that come after
			clearAfcPicks(3);

		}else if(id == "vtAWC36"){
			//if the 6 seed is picked then it plays the 1 seed in DIV (vtADIV1)
			vtADIV1.innerHTML = objTd.innerHTML;
			vtADIV1.setAttribute("teamID", vtAWC36.getAttribute("teamID"));
			frmPostPicks.id_AWC36.value = vtAWC36.getAttribute("teamID");
            frmPostPicks.id_AvtDiv1.value = vtAWC36.getAttribute("teamID");
			//if they changed the winner of this game, we need to clear out the afc picks that come after
			clearAfcPicks(3);

		} else if(id == "htNWC36"){
			//if the 3 seed is picked then it plays the 2 seed in DIV (vtNDIV2)
			vtNDIV2.innerHTML = objTd.innerHTML;
			vtNDIV2.setAttribute("teamID",htNWC36.getAttribute("teamID"));
			frmPostPicks.id_NWC36.value = htNWC36.getAttribute("teamID");
            frmPostPicks.id_NvtDiv2.value = htNWC36.getAttribute("teamID");
			clearNfcPicks(3);

		}else if(id == "vtNWC36"){
			vtNDIV1.innerHTML = objTd.innerHTML;
			vtNDIV1.setAttribute("teamID",vtNWC36.getAttribute("teamID"));
			frmPostPicks.id_NWC36.value = vtNWC36.getAttribute("teamID");
            frmPostPicks.id_NvtDiv1.value = vtNWC36.getAttribute("teamID");
			clearNfcPicks(3);

		}else if(id == "htAWC45") {
		    // need to check the AWC36 game, if 6 is picked then the winner plays the 2 seed (vtADIV2)
		    if(vtADIV1.getAttribute("teamID") == vtAWC36.getAttribute("teamID")){
			    vtADIV2.innerHTML = objTd.innerHTML;
			    vtADIV2.setAttribute("teamID", htAWC45.getAttribute("teamID"));
    			frmPostPicks.id_AvtDiv2.value = htAWC45.getAttribute("teamID");
            }else{
			    vtADIV1.innerHTML = objTd.innerHTML;
			    vtADIV1.setAttribute("teamID", htAWC45.getAttribute("teamID"));
    			frmPostPicks.id_AvtDiv1.value = htAWC45.getAttribute("teamID");
            }
            frmPostPicks.id_AWC45.value = htAWC45.getAttribute("teamID");
			//if they changed the winner of this game, we need to clear out the afc picks that come after
			clearAfcPicks(3);

		}else if(id == "vtAWC45"){
		    // need to check the AWC36 game, if 6 is picked then the winner plays the 2 seed (vtADIV2)
		    if(vtADIV1.getAttribute("teamID") == vtAWC36.getAttribute("teamID")){
    			vtADIV2.innerHTML = objTd.innerHTML;
    			vtADIV2.setAttribute("teamID", vtAWC45.getAttribute("teamID"));
    			frmPostPicks.id_AvtDiv2.value = vtAWC45.getAttribute("teamID");
            }else{
    			vtADIV1.innerHTML = objTd.innerHTML;
    			vtADIV1.setAttribute("teamID", vtAWC45.getAttribute("teamID"));
    			frmPostPicks.id_AvtDiv1.value = vtAWC45.getAttribute("teamID");
            }
			frmPostPicks.id_AWC45.value = vtAWC45.getAttribute("teamID");
			//if they changed the winner of this game, we need to clear out the afc picks that come after
			clearAfcPicks(3);

		}else if(id == "htNWC45"){
		    // need to check the NWC36 game, if 6 is picked then the winner plays the 2 seed (vtNDIV2)
		    if(vtNDIV1.getAttribute("teamID") == vtNWC36.getAttribute("teamID")){
                vtNDIV2.innerHTML = objTd.innerHTML;
                vtNDIV2.setAttribute("teamID", htNWC45.getAttribute("teamID"));
    			frmPostPicks.id_NvtDiv2.value = htNWC45.getAttribute("teamID");
            }else{
                vtNDIV1.innerHTML = objTd.innerHTML;
                vtNDIV1.setAttribute("teamID", htNWC45.getAttribute("teamID"));
    			frmPostPicks.id_NvtDiv1.value = htNWC45.getAttribute("teamID");
            }
			frmPostPicks.id_NWC45.value = htNWC45.getAttribute("teamID");
			clearNfcPicks(3);

		}else if(id == "vtNWC45"){
		    if(vtNDIV1.getAttribute("teamID") == vtNWC36.getAttribute("teamID")){
                vtNDIV2.innerHTML = objTd.innerHTML;
                vtNDIV2.setAttribute("teamID", vtNWC45.getAttribute("teamID"));
    			frmPostPicks.id_NvtDiv2.value = vtNWC45.getAttribute("teamID");
            }else{
                vtNDIV1.innerHTML = objTd.innerHTML;
                vtNDIV1.setAttribute("teamID", vtNWC45.getAttribute("teamID"));
    			frmPostPicks.id_NvtDiv1.value = vtNWC45.getAttribute("teamID");
            }
			frmPostPicks.id_NWC45.value = vtNWC45.getAttribute("teamID");
			clearNfcPicks(3);

		} else if(id == "htADIV1") {
			//they picked this 1 seed to go to the conference championship game
			htACONF.innerHTML = htADIV1.innerHTML;
            htACONF.setAttribute("teamID",htADIV1.getAttribute("teamID"));
			frmPostPicks.id_ADIV1.value = htADIV1.getAttribute("teamID");

			//if they changed the winner of this game, we need to clear out the afc picks that come after
			clearAfcPicks(4);

		} else if(id == "vtADIV1") {
			//they picked the winner of the 4/5 game to win the next round
			htACONF.innerHTML = vtADIV1.innerHTML;
            htACONF.setAttribute("teamID",vtADIV1.getAttribute("teamID"));
			frmPostPicks.id_ADIV1.value = vtADIV1.getAttribute("teamID");

			//if they changed the winner of this game, we need to clear out the afc picks that come after
			clearAfcPicks(4);

		} else if(id == "htNDIV1") {
			htNCONF.innerHTML = htNDIV1.innerHTML;
			htNCONF.setAttribute("teamID",htNDIV1.getAttribute("teamID"));
			frmPostPicks.id_NDIV1.value = htNDIV1.getAttribute("teamID");
			clearNfcPicks(4);

		} else if(id == "vtNDIV1") {
			htNCONF.innerHTML = vtNDIV1.innerHTML;
			htNCONF.setAttribute("teamID",vtNDIV1.getAttribute("teamID"));
			frmPostPicks.id_NDIV1.value = vtNDIV1.getAttribute("teamID");
			clearNfcPicks(4);

		} else if(id == "htADIV2") {
			vtACONF.innerHTML = htADIV2.innerHTML;
			vtACONF.setAttribute("teamID",htADIV2.getAttribute("teamID"));
			frmPostPicks.id_ADIV2.value = htADIV2.getAttribute("teamID");
			clearAfcPicks(4);

		} else if(id == "vtADIV2") {
			vtACONF.innerHTML = vtADIV2.innerHTML;
			vtACONF.setAttribute("teamID", htADIV2.getAttribute("teamID"));
			frmPostPicks.id_ADIV2.value = htADIV2.getAttribute("teamID");
			clearAfcPicks(4);

		} else if(id == "htNDIV2") {
			vtNCONF.innerHTML = htNDIV2.innerHTML;
			vtNCONF.setAttribute("teamID", htNDIV2.getAttribute("teamID"));
			frmPostPicks.id_NDIV2.value = htNDIV2.getAttribute("teamID");
			clearNfcPicks(4);

		} else if(id == "vtNDIV2") {
			vtNCONF.innerHTML = vtNDIV2.innerHTML;
			vtNCONF.setAttribute("teamID", vtNDIV2.getAttribute("teamID"));
			frmPostPicks.id_NDIV2.value = vtNDIV2.getAttribute("teamID");
			clearNfcPicks(4);

		} else if(id == "htACONF") {
			atSB.innerHTML = htACONF.innerHTML;
			atSB.setAttribute("teamID", htACONF.getAttribute("teamID"));
			frmPostPicks.id_ACONF.value = htACONF.getAttribute("teamID");
			clearAfcPicks(5);

		} else if(id == "vtACONF") {
			atSB.innerHTML = vtACONF.innerHTML;
			atSB.setAttribute("teamID", vtACONF.getAttribute("teamID"));
			frmPostPicks.id_ACONF.value = vtACONF.getAttribute("teamID");
			clearAfcPicks(5);

		} else if(id == "htNCONF") {
			ntSB.innerHTML = htNCONF.innerHTML;
			ntSB.setAttribute("teamID", htNCONF.getAttribute("teamID"));
			frmPostPicks.id_NCONF.value = htNCONF.getAttribute("teamID");
			clearNfcPicks(5);

		} else if(id == "vtNCONF") {
			ntSB.innerHTML = vtNCONF.innerHTML;
			ntSB.setAttribute("teamID", vtNCONF.getAttribute("teamID"));
			frmPostPicks.id_NCONF.value = vtNCONF.getAttribute("teamID");
			clearNfcPicks(5);

		} else if(id == "atSB") {
			superChamp.innerHTML = atSB.innerHTML;
			superChamp.setAttribute("teamID", atSB.getAttribute("teamID"));
			frmPostPicks.id_SB.value = atSB.getAttribute("teamID");

		} else if(id == "ntSB") {
			superChamp.innerHTML = ntSB.innerHTML;
			superChamp.setAttribute("teamID", ntSB.getAttribute("teamID"));
			frmPostPicks.id_SB.value = ntSB.getAttribute("teamID");
		}
	}
}

function clearAfcPicks(roundNumber){
	if(roundNumber <= 3){
		htACONF.innerHTML = "TBD";
		vtACONF.innerHTML = "TBD";
		frmPostPicks.id_ADIV1.value = "";
		frmPostPicks.id_ADIV2.value = "";
	}

	if(roundNumber <= 4){
		atSB.innerHTML = "TBD";
		frmPostPicks.id_ACONF.value = "";
	}

	//we're always clearing the superbowl rounds
	superChamp.innerHTML = "TBD";
	frmPostPicks.id_points.value = "";
	frmPostPicks.id_SB.value = "";
}

function clearNfcPicks(roundNumber){
	if(roundNumber <= 3){
		htNCONF.innerHTML = "TBD";
		vtNCONF.innerHTML = "TBD";
		frmPostPicks.id_NDIV1.value = "";
		frmPostPicks.id_NDIV2.value = "";
	}

	if(roundNumber <= 4){
		ntSB.innerHTML = "TBD";
		frmPostPicks.id_NCONF.value = "";
	}

	//we're always clearing the superbowl rounds
	superChamp.innerHTML = "TBD";
	frmPostPicks.id_points.value = "";
	frmPostPicks.id_SB.value = "";
}

function savePicks(){
	var bRet;
	var bPageValid;

	//now validate the page
	bPageValid = validatePage();
	bRet = bPageValid;
	if(bPageValid)
	{
		bPicksChanged = false;
//		frmPostPicks.id_Mode.value = "save";
	}

	return bRet;
}

// TODO: does this need to be updated for django version?
function validatePage(){
	//make sure they've made all the picks necessary (and entered points)
	var bRet = true;
	var sMsg = "";
	var afcValid = true;
	var nfcValid = true;
	var tempValue1 = "";
	var tempValue2 = "";

	tempValue1 = frmPostPicks.id_AWC45.value;
	if(tempValue1 == "" || tempValue1 == "undefined"){
		afcValid = false;
		sMsg += "Pick a winner for the AFC #4 vs #5 game\n";
	}

	tempValue1 = frmPostPicks.id_ADIV2.value;
	if(tempValue1 == "" || tempValue1 == "undefined"){
		afcValid = false;
		sMsg += "Pick a winner for the AFC #3 vs #6 game\n";
	}

	tempValue1 = frmPostPicks.id_NDIV1.value;
	if(tempValue1 == "" || tempValue1 == "undefined"){
		nfcValid = false;
		sMsg += "Pick a winner for the NFC #4 vs #5 game\n";
	}

	tempValue1 = frmPostPicks.id_NWC36.value;
	if(tempValue1 == "" || tempValue1 == "undefined"){
		nfcValid = false;
		sMsg += "Pick a winner for the NFC #3 vs #6 game\n";
	}

	if(afcValid){
		//they've made picks for the first round, so check the next round
		tempValue1 = frmPostPicks.id_ADIV1.value;
		tempValue2 = frmPostPicks.id_ADIV2.value;
		if(tempValue1 == "" || tempValue1 == "undefined" || tempValue2  == "" || tempValue2 == "undefined"){
			afcValid = false;
			sMsg += "Pick winners for the AFC Divisional Playoff games\n";
		}
	}

	if(nfcValid){
		//they've made picks for the first round, so check the next round
		tempValue1 = frmPostPicks.id_NDIV1.value;
		tempValue2 = frmPostPicks.id_NDIV2.value;
		if(tempValue1 == "" || tempValue1 == "undefined" || tempValue2  == "" || tempValue2 == "undefined"){
			nfcValid = false;
			sMsg += "Pick winners for the NFC Divisional Playoff games\n";
		}
	}

	if(afcValid){
		//they've made picks for the second round, so check the next round
		tempValue1 = frmPostPicks.id_ACONF.value;
		if(tempValue1 == "" || tempValue1 == "undefined"){
			afcValid = false;
			sMsg += "Pick a winner for the AFC Conference Championship game\n";
		}
	}

	if(nfcValid){
		//they've made picks for the second round, so check the next round
		tempValue1 = frmPostPicks.id_NCONF.value;
		if(tempValue1 == "" || tempValue1 == "undefined"){
			nfcValid = false;
			sMsg += "Pick a winner for the NFC Conference Championship game\n";
		}
	}

	bRet = afcValid && nfcValid;

	//if everything else was good, check that they've picked a super bowl winner and picked points
	if(bRet){
		tempValue1 = frmPostPicks.id_SB.value;
		if(tempValue1 == "" || tempValue1 == "undefined"){
			bRet = false;
			sMsg += "Pick a winner for the Super Bowl game\n";
		}

		if(frmPostPicks.id_points.value == ""){
			bRet = false;
			sMsg += "Enter a number for the Total Points of the Super Bowl\n";
		} else {
			//also check to make sure that the points game total is a number
			var nums = /^[0-9]*$/;
			if (nums.test(frmPostPicks.id_points.value) == false)
			{
				sMsg += "Enter a number for the Total Points of the Super Bowl\n";
				bRet = false;
			}

		}
	}

	if(sMsg != ""){
		alert(sMsg);
	}

	return bRet;
}

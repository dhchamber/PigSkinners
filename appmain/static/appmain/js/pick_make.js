$(function () {
    // get game links and attach the `click` handler to them
    $('.Game1').on('click', function (e) {
        e.preventDefault();  // prevent default behaviour of link

        var team_selected = $(this).attr('team');  // get team selected and set it for the row
        $('#Selected1').val(team_selected);
        $('.Game1').css('background-color', 'transparent');  // change the background to transparent for the row
        $(this).css('background-color', 'lightblue');          // set the background of the selected team for the game
    });

    $('.Game2').on('click', function (e) {
        e.preventDefault();  // prevent default behaviour of link

        var team_selected = $(this).attr('team');  // get team selected and set it for the row
        $('#Selected2').val(team_selected);

        $('.Game2').css('background-color', 'transparent');  // change the background to transparent for the row
        $(this).css('background-color', 'lightblue');
    });
    $('.Game3').on('click', function (e) {
        e.preventDefault();  // prevent default behaviour of link

        var team_selected = $(this).attr('team');  // get team selected and set it for the row
        $('#Selected3').val(team_selected);

        $('.Game3').css('background-color', 'transparent');  // change the background to transparent for the row
        $(this).css('background-color', 'lightblue');
    });
    $('.Game4').on('click', function (e) {
        e.preventDefault();  // prevent default behaviour of link

        var team_selected = $(this).attr('team');  // get team selected and set it for the row
        $('#Selected4').val(team_selected);

        $('.Game4').css('background-color', 'transparent');  // change the background to transparent for the row
        $(this).css('background-color', 'lightblue');
    });
    $('.Game5').on('click', function (e) {
        e.preventDefault();  // prevent default behaviour of link

        var team_selected = $(this).attr('team');  // get team selected and set it for the row
        $('#Selected5').val(team_selected);

        $('.Game5').css('background-color', 'transparent');  // change the background to transparent for the row
        $(this).css('background-color', 'lightblue');
    });
    $('.Game6').on('click', function (e) {
        e.preventDefault();  // prevent default behaviour of link

        var team_selected = $(this).attr('team');  // get team selected and set it for the row
        $('#Selected6').val(team_selected);

        $('.Game6').css('background-color', 'transparent');  // change the background to transparent for the row
        $(this).css('background-color', 'lightblue');
    });
    $('.Game7').on('click', function (e) {
        e.preventDefault();  // prevent default behaviour of link

        var team_selected = $(this).attr('team');  // get team selected and set it for the row
        $('#Selected7').val(team_selected);

        $('.Game7').css('background-color', 'transparent');  // change the background to transparent for the row
        $(this).css('background-color', 'lightblue');
    });
    $('.Game8').on('click', function (e) {
        e.preventDefault();  // prevent default behaviour of link

        var team_selected = $(this).attr('team');  // get team selected and set it for the row
        $('#Selected8').val(team_selected);

        $('.Game8').css('background-color', 'transparent');  // change the background to transparent for the row
        $(this).css('background-color', 'lightblue');
    });
    $('.Game9').on('click', function (e) {
        e.preventDefault();  // prevent default behaviour of link

        var team_selected = $(this).attr('team');  // get team selected and set it for the row
        $('#Selected9').val(team_selected);

        $('.Game9').css('background-color', 'transparent');  // change the background to transparent for the row
        $(this).css('background-color', 'lightblue');
    });
    $('.Game10').on('click', function (e) {
        e.preventDefault();  // prevent default behaviour of link

        var team_selected = $(this).attr('team');  // get team selected and set it for the row
        $('#Selected10').val(team_selected);

        $('.Game10').css('background-color', 'transparent');  // change the background to transparent for the row
        $(this).css('background-color', 'lightblue');
    });
    $('.Game10').on('click', function (e) {
        e.preventDefault();  // prevent default behaviour of link

        var team_selected = $(this).attr('team');  // get team selected and set it for the row
        $('#Selected10').val(team_selected);

        $('.Game10').css('background-color', 'transparent');  // change the background to transparent for the row
        $(this).css('background-color', 'lightblue');
    });
    $('.Game11').on('click', function (e) {
        e.preventDefault();  // prevent default behaviour of link

        var team_selected = $(this).attr('team');  // get team selected and set it for the row
        $('#Selected11').val(team_selected);

        $('.Game11').css('background-color', 'transparent');  // change the background to transparent for the row
        $(this).css('background-color', 'lightblue');
    });
    $('.Game12').on('click', function (e) {
        e.preventDefault();  // prevent default behaviour of link

        var team_selected = $(this).attr('team');  // get team selected and set it for the row
        $('#Selected12').val(team_selected);

        $('.Game12').css('background-color', 'transparent');  // change the background to transparent for the row
        $(this).css('background-color', 'lightblue');
    });
    $('.Game13').on('click', function (e) {
        e.preventDefault();  // prevent default behaviour of link

        var team_selected = $(this).attr('team');  // get team selected and set it for the row
        $('#Selected13').val(team_selected);

        $('.Game13').css('background-color', 'transparent');  // change the background to transparent for the row
        $(this).css('background-color', 'lightblue');
    });
    $('.Game14').on('click', function (e) {
        e.preventDefault();  // prevent default behaviour of link

        var team_selected = $(this).attr('team');  // get team selected and set it for the row
        $('#Selected14').val(team_selected);

        $('.Game14').css('background-color', 'transparent');  // change the background to transparent for the row
        $(this).css('background-color', 'lightblue');
    });
    $('.Game15').on('click', function (e) {
        e.preventDefault();  // prevent default behaviour of link

        var team_selected = $(this).attr('team');  // get team selected and set it for the row
        $('#Selected15').val(team_selected);

        $('.Game15').css('background-color', 'transparent');  // change the background to transparent for the row
        $(this).css('background-color', 'lightblue');
    });
    $('.Game16').on('click', function (e) {
        e.preventDefault();  // prevent default behaviour of link

        var team_selected = $(this).attr('team');  // get team selected and set it for the row
        $('#Selected16').val(team_selected);

        $('.Game16').css('background-color', 'transparent');  // change the background to transparent for the row
        $(this).css('background-color', 'lightblue');
    });
});

function selectRandomPicks() {
var i;
var sel;

//randomly select a points game value between 30-60 points, but only if they haven't already have selected something
var x = $('#txtPointsTotal').val();
if (!(parseInt(x) > 0)) {
    $('#txtPointsTotal').val(Math.floor((60-29)*Math.random()) + 30);
}

//select random KOTH if it's available
var kothEligible = $('.cboKingOfHillPick').attr('kothEligible');
if(kothEligible == "True" && frmPicks.cboKingOfHillPick.value == "") {
    var upperLimit = frmPicks.cboKingOfHillPick.options.length - 1;
    frmPicks.cboKingOfHillPick.selectedIndex = Math.floor((upperLimit)*Math.random()) + 1;
}

//Select a random pick for each game if there already isn't a pick made
for (i = 1; i <= 16; i++) {
    selTeam = $('#Selected'.concat(i)).val();
    if(!(parseInt(selTeam) > 0)) {
        //generate a random number and see if it is even or odd, even = HOME team, odd = AWAY team
        var random = Math.floor(Math.random()*101);
        if(random % 2 == 0) {
            $('#Game'.concat(i).concat('Home')).click();
        } else {
            $('#Game'.concat(i).concat('Visitor')).click();
        }
    }
}
}

function isDataRow(objRow)
{
	if(objRow.cells.length > 1) {
		if(objRow.cells[1].innerHTML == "&nbsp;&nbsp;") {
			return true;
		} else {
			return false;
		}
	} else {
		return false;
	}
}

function savePicks(bWeekClosed,bKothElibible)
{
	//loop through the picks table and retrieve the ID's of the user's picks
	var bPageValid;
	var bRet, bAllowEdits, bSavePicks;

	//check to see if we allow edits
//	console.log('WeekClosed:', bWeekClosed)
//	bAllowEdits = 'bWeekClosed';
//	if(bWeekClosed == "False") {
//		if(confirm("You are about to submit your picks.\nYou can't change the picks later!") == true)
//			bSavePicks = true;
//		else
//			bSavePicks = false;
//	} else {
//		bSavePicks = true;
//	}

    bSavePicks = true;
	bRet = bSavePicks;
	if(bSavePicks) {
		//now validate the page
		bPageValid = validatePage(bKothElibible);
		bRet = bPageValid;

		if(bPageValid) {
		    console.log('bPageValid True');
    		$('#btnSavePicks1').click();

//			bPicksChanged = false;
//			frmPicks.hidPicksData.value = readPickData();
//			frmPicks.hidPointsGameData.value = readPointsGameData();
//			if(frmPicks.cboKingOfHillPick == undefined) {
//				frmPicks.hidKingOfHillPick.value = "";
//			} else {
//				frmPicks.hidKingOfHillPick.value = frmPicks.cboKingOfHillPick.value;
//			}
//			frmPicks.hidMode.value = "save";
		}
	}
	return bRet;
}

function validatePage(bKothElibible)
{
	var bValid, bForceAllPicks, bAllSelected;
	var i, sErrMsg, kothOnly;

	bForceAllPicks = 'true'  //"<%=cgForceAllPicks%>";
	kingOfTheHillEligible = bKothElibible //"<%=kingOfTheHillEligibleThisWeek%>";
	kothOnly = 'false'  //"<%=kothOnly%>";
	//loop through the table and see which rows are selected
	//initialize boolean
	bAllSelected = true;
	bValid = true;
	if(kothOnly.toLowerCase() == "false") {
		for (let i = 1; i < 17; i++) {
            if($('#Selected'.concat(i)).val() == "") {
                bAllSelected = false;
                break;
            }
		}
	}
	sErrMsg = "";

	//if it's a requirement that all picks be selected then show error message
	if(bForceAllPicks.toLowerCase() == "true") {
		if(bAllSelected == false) {
			sErrMsg = sErrMsg + "\n- Select a winner for all the games.\n";
			bValid = false;
		}

		//also check the "points game total" value
		if(kothOnly.toLowerCase() == "false" && frmPicks.txtPointsTotal.value <= 0 ) {
			sErrMsg = sErrMsg + "\n- Enter a number for the Points Game Total.\n";
			bValid = false;
		}

		//also check the king of the hill pick, if we need to
		if(kingOfTheHillEligible.toLowerCase() == "true") {
			//did they pick a king of the hill team?
			if(frmPicks.cboKingOfHillPick.value == "") {
				sErrMsg = sErrMsg + "\n- Pick a team for the 'King of the Hill' pool.\n";
				bValid = false;
			}
		}
	}

	if(kothOnly.toLowerCase() == "false") {
		//also check to make sure that the points game total is a number
		var nums = /^[0-9]*$/;
		if (nums.test(frmPicks.txtPointsTotal.value) == false) {
			sErrMsg = sErrMsg + "\n- Enter a number for the Points Game Total.";
			bValid = false;
		}
	}

	if(bValid == false) {
//		tblErrorMsg.style.display = "";
//		errMsg.innerHTML = sErrMsg;
        window.alert(sErrMsg);
	}
	return bValid;
}

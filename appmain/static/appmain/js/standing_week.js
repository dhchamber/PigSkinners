var iIntervalId;
var sColor = "white";
var sLoaded = false;
var compareRow;
var iSelectedRows = 0;
var arrSelectedRows = new Array(0);

function window_onload(n)
{
console.log('N: ', n)
    if (n == 0) {
        col = n + 2
    } else {
        col = n + 1
    }
console.log('col: ', col)
    sortTableNum(col);
    sortTableNum(col); // sort descending
console.log('Sorted Desc ', col)
}

// example code coppied from https://www.w3schools.com/howto/howto_js_sort_table.asp
function sortTableNum(n) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;

  table = document.getElementById("tblStats");
  switching = true;
  // Set the sorting direction to ascending:
  dir = "asc";
  /* Make a loop that will continue until
  no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /* Loop through all table rows (except the
    first, which contains table headers): */
    for (i = 3; i < (rows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      x = rows[i].getElementsByClassName("score")[0];
      y = rows[i + 1].getElementsByClassName("score")[0];
//      y = rows[i + 1].getElementsByTagName("TD")[n];
      /* Check if the two rows should switch place,
      based on the direction, asc or desc: */
      if (dir == "asc") {
        if (Number(x.innerHTML) > Number(y.innerHTML)) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if (Number(x.innerHTML) < Number(y.innerHTML)) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /* If a switch has been marked, make the switch
      and mark that a switch has been done: */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      // Each time a switch is done, increase this count by 1:
      switchcount ++;
    } else {
      /* If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again. */
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}

function sortTable(n) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;

  table = document.getElementById("tblStats");
  switching = true;
  // Set the sorting direction to ascending:
  dir = "asc";
  /* Make a loop that will continue until
  no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /* Loop through all table rows (except the
    first, which contains table headers): */
    for (i = 3; i < (rows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      /* Check if the two rows should switch place,
      based on the direction, asc or desc: */
      if (dir == "asc") {
        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /* If a switch has been marked, make the switch
      and mark that a switch has been done: */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      // Each time a switch is done, increase this count by 1:
      switchcount ++;
    } else {
      /* If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again. */
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}

function highlightUserRow()
{
	var userId = "{{ user_picks.user.id }}";
	if(userId != "" && userId != "<%=cgDemoUserId%>")
	{
		var row = document.getElementById("tr" + userId).cells[0];
		while (row.tagName.toUpperCase() != 'TR' && row != null)
			row = document.all ? row.parentElement : row.parentNode;
		userRow = row;
		highlightRow(row);
	}
}

function highlightRow(row)
{
	var userId = "{{ user_picks.user.id }}";
	if (row)
	{
		if(row.bgColor != "yellow")
		{
			row.bgColor = "yellow";
			addSelectedRowAndCompare(row);
			//if we just selected the "third" row, then clear the "compare" highlights
			//if(iSelectedRows == 3)
			//{
			//	clearCompareUsers();
			//}
		}
		else
		{
			if(row.id != "tr" + userId)
			{
				row.bgColor = "white";
				clearSelectedRowAndCompare(row);
			}
		}
	}
}

function clearCompareUsers(row)
{
	var row1 = getRowFromTable(arrSelectedRows[0]);
	var row2 = getRowFromTable(arrSelectedRows[1]);
	var i;
	if(row != undefined)
	{
		row2 = row;
	}

	if(row1 != undefined && row2 != undefined)
	{
		if(row1.cells.length == row2.cells.length)
		{
			for(i = 1; i < row1.cells.length; i++)
			{
				row1.cells[i].bgColor = "";
				row2.cells[i].bgColor = "";
			}
		}
	}
	compareUserPicks();
}

function removeRowFromArray(row)
{
	var i;
	for(i=0; i < arrSelectedRows.length; i++)
	{
		if(row.id == arrSelectedRows[i])
		{
			arrSelectedRows.splice(i, 1);
			break;
		}
	}
}

function addSelectedRowAndCompare(row)
{
	if(row)
	{
		var isCompared = row.getAttribute("isCompared");
		if(isCompared == false || isCompared == "false")
		{
			//add this row to the "selected" array
			arrSelectedRows.splice(iSelectedRows, 1, row.id);
			iSelectedRows += 1;
			row.setAttribute("isCompared", "true");
		}
		compareUserPicks();
	}
}

function clearSelectedRowAndCompare(row)
{
	if(row)
	{
		if(row.getAttribute("isCompared") == true || row.getAttribute("isCompared") == "true")
		{
			//remove this row from the "selected" array
			removeRowFromArray(row);
			iSelectedRows -= 1;
			row.setAttribute("isCompared", "false");
			clearCompareUsers(row);
		}
	}
}

function showAllDiffs()
{
	var text = btnShowDiffs.value;
	if(text == "Show All Diffs")
	{
		//we want to show all the differences
		var table = document.getElementById("tblStats");
		if (table.tHead == null && table.tFoot == null)
		{
			for (var r1 = 0; r1 < table.rows.length; r1++)
			{
				if(table.rows[r1].getAttribute("userRow") != "false")
				{
					var row = table.rows[r1];
					addSelectedRowAndCompare(row);
				}
			}
		}
		else
		{
			for (var t = 0; t < table.tBodies.length; t++)
			{
				for (var r1 = 0; r1 < table.tBodies[t].rows.length; r1++)
				{
					if(table.tBodies[t].rows[r1].getAttribute("userRow") != "false")
					{
						var row = table.tBodies[t].rows[r1];
						addSelectedRowAndCompare(row);
					}
				}
			}
		}

		//now change the text of the button
		btnShowDiffs.value = "Hide All Diffs";
	}
	else
	{
		//we want to hide all the differences
		var table = document.getElementById("tblStats");
		if (table.tHead == null && table.tFoot == null)
		{
			for (var r1 = 0; r1 < table.rows.length; r1++)
			{
				if(table.rows[r1].getAttribute("userRow") != "false")
				{
					var row = table.rows[r1];
					if(row.bgColor != "yellow")
					{
						clearSelectedRowAndCompare(row);
					}
				}
			}
		}
		else
		{
			for (var t = 0; t < table.tBodies.length; t++)
			{
				for (var r1 = 0; r1 < table.tBodies[t].rows.length; r1++)
				{
					if(table.tBodies[t].rows[r1].getAttribute("userRow") != "false")
					{
						var row = table.tBodies[t].rows[r1];
						if(row.bgColor != "yellow")
						{
							clearSelectedRowAndCompare(row);
						}
					}
				}
			}
		}

		//now change the text of the button
		btnShowDiffs.value = "Show All Diffs";
	}

}

function compareUserPicks()
{
	//row1 is always the current user's row
	var row1 = getRowFromTable(arrSelectedRows[0]);
	for(rowIndex = 1; rowIndex < arrSelectedRows.length; rowIndex ++)
	{
		var row2 = getRowFromTable(arrSelectedRows[rowIndex]);
		var i;
		if(row1 != undefined && row2 != undefined)
		{
			if(row1.cells.length == row2.cells.length)
			{
				for(i = 1; i < row1.cells.length; i++)
				{
					var cell1 = row1.cells[i];
					var cell2 = row2.cells[i];
					if(isNaN(cell1.innerText) == true && isNaN(cell2.innerText) == true)
					{
						if(cell1.innerText != cell2.innerText)
						{
							cell1.bgColor = "red";
							cell2.bgColor = "red";
						}
					}
					else
					{
						//break out of the loop, we've hit the "number" columns
						break;
					}
				}
			}
		}
	}
}

function getRowFromTable(rowId)
{
	var r = 0;
	if(rowId != undefined && rowId != "")
	{
		var table = document.getElementById("tblStats");
		if (table.tHead == null && table.tFoot == null)
		{
			for (var r1 = 0; r1 < table.rows.length; r1++)
			{
				if(table.rows[r1].getAttribute("userRow") != "false")
				{
					var row = table.rows[r1];
					if(rowId == row.id)
					{
						return row;
					}
					r++;
				}
			}
		}
		else
		{
			for (var t = 0; t < table.tBodies.length; t++)
			{
				for (var r1 = 0; r1 < table.tBodies[t].rows.length; r1++)
				{
					if(table.tBodies[t].rows[r1].getAttribute("userRow") != "false")
					{
						var row = table.tBodies[t].rows[r1];
						if(rowId == row.id)
						{
							return row;
						}
						r++;
					}
				}
			}
		}
	}
}

function highlightWinnerRows (sWinnerIDs)
{
	var delimiter = "<%=cgDelimiter%>";
	var userId = "<%=userID%>";
	var iNumOfWinners;
	var arrWinners;
	var element;

	//we don't want to do anything here if there is no winner
	arrWinners = sWinnerIDs.split(delimiter);
	iNumOfWinners = arrWinners.length;
	for(var i=0; i < iNumOfWinners; i++)
	{
		element = document.getElementById("tr" + arrWinners[i]).cells[0];

		if(sColor == "red")
		{
			if(arrWinners[i] == userId)
				sColor = "yellow";
			else
				sColor = "white";
		}
		else
		{
			sColor = "red";
		}
		while (element.tagName.toUpperCase() != 'TR' && element != null)
		  element = document.all ? element.parentElement : element.parentNode;
		if (element)
		  element.bgColor = sColor;
	}
}

function window_onunload()
{
	if(sLoaded)
	{
		window.clearInterval(iIntervalID);
	}
}

function TooltipText(objTD)
{
	var sRet = "";
	sRet = "Click here to sort list by people who picked the " + objTD;
	return sRet;
}


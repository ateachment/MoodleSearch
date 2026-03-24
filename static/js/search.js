// search.js - JavaScript code for handling search functionality on the client side

const fetchDataBtn = document.querySelector("#fetchdata");
const result = document.getElementById("result");
/*
var timeleft = 10;
var downloadTimer = setInterval(function() {
  result.innerText = timeleft;
  if(timeleft <= 0) {
    clearIntervall(downloadTimer);
  }
  timeleft -= 1;
}, 1000);
*/

function getFullUrlText(data, startIndex) {
  var fullUrlText = "";
  for (var i = startIndex; i < data.shortText.length; i++) {
    if (data.shortText[i].trim() !== "") {
      fullUrlText += " > " + data.shortText[i];
    }
  }
  return fullUrlText;
}




function findFirstNonEmptyString(arr, startIndex = 0) {
  for (let i = startIndex; i < arr.length; i++) {
    if (arr[i].trim() !== "") {
      return arr[i];
    }
  }
  return "empty"; // Return an empty string if no non-empty string is found
}


function appendData(data) {
  //var mainContainer = document.getElementById("myData");
  if(data.length > 0)
    for (var i = 0; i < data.length; i++) 
    {
      // alert(data[i].shortText.length + " " + data[i].shortText);
      var urlText = "";  // "<span>"+data[i].link + "</span>";
      var fullUrlText = "";
      var resultHeader = "<img class='icon' src='static/images/course.svg' alt='Course'>" + data[i].shortText[0];
      var snippet = "";
      var icon = "";
      link = data[i].link;
      if (link.includes("/course/view.php")) {                        // course
          icon = "";
          snippet = findFirstNonEmptyString(data[i].shortText, 1);
      } else if(link.includes("/course/section.php")) {               // section
          icon = "<img class='icon' src='static/images/section.svg' alt='Section'>";
          fullUrlText += getFullUrlText(data[i], 1);
          snippet = icon + findFirstNonEmptyString(data[i].shortText, 1);
      } else if(link.includes("/mod/page/view.php")) {                // page
          icon = "<img class='icon' src='static/images/page.svg' alt='Page'>";
          fullUrlText += getFullUrlText(data[i], 2);
          snippet = icon + findFirstNonEmptyString(data[i].shortText, 2);
      }
      else {    
          alert("Unknown type of link: " + data[i].link);
      }

   
      urlText += "<div class='resultHeader'>" + resultHeader + "</div>\n";
      urlText += "<div class='snippet'>" + snippet + "</div>\n";   
      urlText += "<span>" + fullUrlText + "</span>\n";
      var div = document.createElement("div");  
      div.className += " link";
      div.innerHTML = "<a href='" + data[i].link + "' target='_blank' title='Similarity: " + data[i].similarity + "  Index: " + data[i].index + "'>" + urlText + "</a> ";
      result.appendChild(div);
    }
  else
  {
    var div = document.createElement("div");
    div.className += " noResult";
    div.innerHTML = "Nothing found!";
    result.appendChild(div);
  }
}

// gets data from API and sets the content of #result div
async function getData() {
  const queryString = new URLSearchParams(window.location.search); //eick-at or wvs-ffm
  let search = document.getElementById("search").value;
  let data = '{ "search" : "' + search + '", "i" : "' + queryString.get('i') + '"} '
  //data.append('search', search);
  //data.append('i', queryString.get('i')); 
  // alert(data);
  if(document.getElementById("search").value == "")
    alert("Please enter search words!");
  else
  {
    result.innerText = "Loading 10 sec ...";
    try {
      const res = await fetch("search", {
                                method: 'POST',
                                headers: {
                                  'Content-Type': 'application/json; charset=utf-8'
                                },
                                body: JSON.stringify(data)
                                });
      const jsonResult = await res.json();
      result.innerText = "";
      appendData(jsonResult)
    } catch (error) {
      console.log(error);
    }
  }
}

// add event listener for #fetchdata button
fetchDataBtn.addEventListener("click", getData);
document.addEventListener("keydown", function (e) {
  if(13 == e.keyCode) {
    if(document.getElementById("search").value == "")
      alert("Please enter search words!");
    else
      getData();
  }
});
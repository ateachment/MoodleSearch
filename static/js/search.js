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

function appendData(data) {
  //var mainContainer = document.getElementById("myData");
  if(data.length > 0)
    for (var i = 0; i < data.length; i++) 
    {
      // alert(data[i].shortText.length + " " + data[i].shortText);
      var urlText = "<span>"+data[i].link + "</span>";
      var fullUrlText = "";
      var resultHeader = "";
      var snippet = "";
      switch(data[i].shortText.length) {    
        case 2:                           // course
          resultHeader = data[i].shortText[0];
          snippet = data[i].shortText[1];
          break;
        case 4:                           // section
          resultHeader = data[i].shortText[2];
          fullUrlText += " > " + data[i].shortText[0];
          snippet = data[i].shortText[3];
          break;
        case 4:                           // page title
          resultHeader = data[i].shortText[3];
          fullUrlText += " > " + data[i].shortText[1] + " > " + data[i].shortText[2];
          break;
        case 5:                           // page content
          resultHeader = data[i].shortText[3];
          fullUrlText += " > " + data[i].shortText[0] + " > " + data[i].shortText[2];
          snippet = data[i].shortText[4];
          break;
      }
      urlText += "<span>" + fullUrlText + "</span>\n";
      urlText += "<h2>" + resultHeader + "</h2>\n";
      urlText += "<div class='snippet'>" + snippet + "</div>\n";   
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
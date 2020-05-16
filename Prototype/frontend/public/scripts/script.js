function init(){
  document.getElementById('upload-data-text').style.display = "none";
  document.getElementById('upload-data-form').style.display = "none";

}

function uploadFreightdata(){
  document.getElementById('intro-text').style.display = "none";
  document.getElementById('intro-buttons').style.display = "none";
  document.getElementById('upload-data-text').style.display = "block";
  document.getElementById('upload-data-form').style.display = "block";

}

window.onload = init;

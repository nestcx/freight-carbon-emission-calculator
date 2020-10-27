"use strict";

var modalElement = document.getElementById('modal-file-upload');
var blackBg = document.getElementById('black-out-screen');



blackBg.onclick = closeModal;

document.addEventListener('keyup', function(e) {
  if (e.key === 'Escape' && modalElement.classList.contains('--modal-active')) {
    closeModal();
  }
});

function displayModal() {
  modalElement.classList.add('--modal-active');
  blackBg.classList.add('--modal-active');

  // Get dimensions of modal so you can place it in the centre
  var modalElementDimensions = modalElement.getBoundingClientRect();
  modalElement.style.top = (window.innerHeight / 2) - (modalElementDimensions.height / 2) + 'px';
  modalElement.style.left = (window.innerWidth / 2) - (modalElementDimensions.width / 2) + 'px';
}

function closeModal() {
  modalElement.classList.remove('--modal-active');
  blackBg.classList.remove('--modal-active');
}

//filter shipments 

function uploadShipment() {
  var formData = new FormData();
  var file = document.getElementById('shipments')
  formData.append('file', file.files[0])

  closeModal()
  createFlashMessage()
  
  axios.post('/shipments', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  .then(function (response) {
    if (response.status = 200) {
      location.reload()
    }
  })
  .catch(function (error) {
    console.log(error)
  })
}

// Create a flash message on the bottom of the screen, that will dissapear after a few seconds
function createFlashMessage() {
  var pageContainer = document.getElementsByClassName('page-container')[0]
  
  // We want to place the flash message just above the footer, so get footer and it's boundbox
  var footer = document.getElementsByClassName('footer')[0]
  var footerRect = footer.getBoundingClientRect()

  var flashToast = document.createElement('div')
  flashToast.classList.add('flash--toast')

  flashToast.style.bottom = footerRect.height + 'px' // Place the message just above the footer

  var text = document.createElement('p')
  text.innerText = 'Uploading shipments. This may take a while.'

  flashToast.appendChild(text)
  pageContainer.appendChild(flashToast)
  
  flashToast.addEventListener('click', hideFlashMessage)
  setTimeout(hideFlashMessage, 6000)
}


function hideFlashMessage() {
  var pageContainer = document.getElementsByClassName('page-container')[0]
  var flashMessage = document.getElementsByClassName('flash--toast')[0]

  flashMessage.classList.add('flash--toast--transparent')

  // Remove from the DOM after the animation is over, just to avoid any unforeseen issues
  setTimeout(function() {
    pageContainer.removeChild(flashMessage)
  }, 1000)
}
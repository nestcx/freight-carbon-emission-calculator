function back_to_tools() {
    window.location.href = '/tools'
}

function myFunction() {

    // get string from textbox
    input = document.getElementById('shipment1').value
    axios.get('/tools/compare/search?q=' + input)
    .then((response) => {
        console.log(response.data)

    })
    .catch((error) => {
        console.log(error)
    })

    console.log(input)
}
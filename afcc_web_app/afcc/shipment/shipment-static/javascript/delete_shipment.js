function deleteShipment(shipment_id) {
    axios.delete('/shipments/' + shipment_id)
    .then((response) => {
        console.log(response.data)
        window.location.href = '/shipments'

    })
    .catch((error) => {
        console.log(error)
        window.location.href = '/shipments'
    })
}
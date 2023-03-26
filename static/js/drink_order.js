
window.onload = function() {
    inputs = document.getElementsByTagName("input")
    for(let i = 0; i < inputs.length; i++) {
        inputs[i].setAttribute("class", "form-check-input")
    };
}
  

function drink_parse(btn,id,drink_name,drink_price) {
    let drinkInput = document.getElementById("drinkIdInput")
    let orderDesc = document.getElementById("orderDesc")
    drinkInput.value = id 
    orderDesc.innerHTML = `Je gaat <b>${drink_name}</b> bestellen voor €${drink_price}`
}


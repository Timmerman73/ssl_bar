
window.onload = function() {
    inputs = document.getElementsByTagName("input")
    for(let i = 0; i < inputs.length; i++) {
        inputs[i].setAttribute("class", "form-check-input")
    };
}
  

function drink_parse(btn,id,naam) {
    savebtn = document.getElementById("savebtn")
    orderDesc = document.getElementById("orderDesc")
    console.log(btn,id,naam)
}


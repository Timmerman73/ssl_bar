function drink_parse() {
    let conf = document.getElementById("conftext")
    const drink = document.getElementById("id_drink")
    conf.innerHTML = `Je gaat ${drink.options[drink.selectedIndex].text} verwijderen! `
}
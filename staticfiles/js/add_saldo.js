function saldo_parse() {
    let conf = document.getElementById("conftext")
    const amount = document.getElementById("id_amount").value
    const user_for = document.getElementById("id_user")
    conf.innerHTML = `Je gaat €${amount} toevoegen aan het saldo van ${user_for.options[user_for.selectedIndex].text}`
}
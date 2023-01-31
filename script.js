function enable() {
    const btnEnabled = document.getElementById("button");
    const checkbox = document.getElementById("checkbox");
    if (checkbox.checked){
        btnEnabled.removeAttribute("disabled");
    }

}


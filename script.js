function enable() {
    const btnEnabled = document.getElementById("button");
    const checkbox = document.getElementById("checkbox");
    if (checkbox.checked){
        btnEnabled.removeAttribute("disabled");
    }

}

const addBtn = document.querySelector(".add");

const input = document.querySelector(".inp-group");

function addInput() {
    const ExpenseName = document.createElement("select");
    ExpenseName.type="text";
    Currency.placeholder="Expense name"

    const Currency = document.createElement("select");
    Currency.type="text";
    Currency.placeholder="Currency"

    const Amount = document.createElement("input");
    Amount.type="integer";
    Amount.placeholder="00.00"

    const AddExpense = document.createElement("submit");

    const btn = document.createElement("a");
    btn.className = "delete";
    btn.innerHTML = "&times";

    const flex = document.createElement("div");
    flex.className = "flex";
    
    input.appendChild(flex);
    flex.appendChild(ExpenseName);
    flex.appendChild(Currency);
    flex.appendChild(Amount);
    flex.appendChild(AddExpense);
    flex.appendChild(btn);


}
addBtn.addEventListener("click", addInput);

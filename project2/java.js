setTimeout(function() {
    alert("Chào mừng bạn đến với trang web của chúng tôi!");
}, 3000);
const decreaseBtn = document.getElementById("decrease");
const increaseBtn = document.getElementById("increase");
const valueInput = document.getElementById("value");

increaseBtn.addEventListener("click", () => {
    let value = parseInt(valueInput.value);
    valueInput.value = value + 1;
});

decreaseBtn.addEventListener("click", () => {
    let value = parseInt(valueInput.value);
    if (value > 1) { // không cho nhỏ hơn 1
        valueInput.value = value - 1;
    }
});
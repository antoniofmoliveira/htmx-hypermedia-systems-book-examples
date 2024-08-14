const counterOutput = document.querySelector("#my-output")
const incrementBtn = document.querySelector(".counter .increment-btn")

incrementBtn.addEventListener("click", e => {
    counterOutput.innerHTML++
})
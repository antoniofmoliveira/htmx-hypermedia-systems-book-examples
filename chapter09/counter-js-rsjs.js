document.querySelectorAll("[data-counter-js-rsjs]")
  .forEach(el => {
    const output = el.querySelector("[data-counter-output]")
    const increment = el.querySelector("[data-counter-increment]");

    increment.addEventListener("click", e => output.textContent++);
  });
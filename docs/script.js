/* Progressive enhancement only. This static preview never predicts a value. */
'use strict';
document.documentElement.classList.add('js');
const menuButton = document.querySelector('.menu-toggle');
const menu = document.querySelector('#nav-links');
function closeMenu() {
  menu.classList.remove('is-open');
  menuButton.setAttribute('aria-expanded', 'false');
}
menuButton.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') !== 'true';
  menuButton.setAttribute('aria-expanded', String(open));
  menu.classList.toggle('is-open', open);
});
menu.addEventListener('click', (event) => {
  if (event.target.closest('a')) closeMenu();
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
    closeMenu();
    menuButton.focus();
  }
});
const form = document.querySelector('#preview-form');
const inputs = [...form.querySelectorAll('input[type="range"]')];
function updateValue(input) {
  const digits = Number(input.dataset.digits);
  const value = Number(input.value).toLocaleString('en-US', {
    minimumFractionDigits: digits, maximumFractionDigits: digits
  });
  document.getElementById(`${input.id}-value`).textContent = `${value} ${input.dataset.unit}`;
  input.setAttribute('aria-valuetext', `${value} ${input.dataset.unit}`);
}
inputs.forEach((input) => {
  updateValue(input);
  input.addEventListener('input', () => updateValue(input));
});
form.addEventListener('submit', (event) => event.preventDefault());
form.addEventListener('reset', () => {
  // Reset default values before refreshing labels, without relying on event timing.
  inputs.forEach((input) => { input.value = input.defaultValue; updateValue(input); });
});

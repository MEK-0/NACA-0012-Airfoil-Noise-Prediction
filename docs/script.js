/* No backend calls: language selection and local form validation only. */
'use strict';
(() => {
  const translations = window.REPORT_TRANSLATIONS;
  if (!translations) return; // The complete English report remains readable.
  let language = 'en';
  let statusKey = '';
  const form = document.getElementById('preview-form');
  const status = document.getElementById('preview-status');
  const languageButtons = document.querySelectorAll('[data-language]');

  function setLanguage(next) {
    if (!Object.hasOwn(translations, next)) return;
    language = next;
    document.documentElement.lang = next;
    document.title = translations[next].page_title;
    document.querySelectorAll('[data-i18n]').forEach((element) => {
      element.textContent = translations[next][element.dataset.i18n];
    });
    document.querySelectorAll('[data-i18n-alt]').forEach((element) => {
      element.alt = translations[next][element.dataset.i18nAlt];
    });
    languageButtons.forEach((button) => {
      button.setAttribute('aria-pressed', String(button.dataset.language === next));
    });
    status.textContent = statusKey ? translations[next][statusKey] : '';
  }

  languageButtons.forEach((button) => {
    button.addEventListener('click', () => setLanguage(button.dataset.language));
  });
  function checkInputs() {
    statusKey = form.checkValidity() ? 'status_valid' : 'status_invalid';
    status.textContent = translations[language][statusKey];
  }
  const checkButton = document.getElementById('check-inputs');
  checkButton.disabled = false;
  checkButton.addEventListener('click', checkInputs);
  // Native validation is queried above; translated feedback stays consistent
  // even when the browser's interface language differs from the report.
  form.noValidate = true;
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    checkInputs();
  });
  function clearStatus() {
    statusKey = '';
    status.textContent = '';
  }
  form.addEventListener('input', clearStatus);
  form.addEventListener('reset', clearStatus);
  setLanguage('en');
})();

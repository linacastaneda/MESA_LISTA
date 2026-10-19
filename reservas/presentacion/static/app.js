'use strict';
// Mejora progresiva: el servidor valida todas las operaciones sin depender de JS.
document.querySelectorAll('form[data-confirm]').forEach((form) => {
  form.addEventListener('submit', (event) => {
    if (!window.confirm(form.dataset.confirm)) event.preventDefault();
  });
});

'use strict';
try {
  if (window.MESALISTA_APP_URL) {
    const url = new URL(window.MESALISTA_APP_URL);
    if (url.protocol !== 'https:') throw new Error('Se requiere HTTPS');
    const link = document.getElementById('abrir-app');
    link.href = url.href;
    link.hidden = false;
    document.getElementById('estado').textContent = 'El botón abre la aplicación en su servidor. Las reservas se guardan allí.';
  }
} catch (_) {
  document.getElementById('estado').textContent = 'La dirección de la aplicación no está configurada correctamente.';
}

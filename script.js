// EVOREHAB landing page

// Reproductor de vídeo dentro de la página (modal), para que al hacer clic
// en un testimonio o historia de Instagram el vídeo se vea sin salir de la web.
document.addEventListener('DOMContentLoaded', function () {
  var modal = document.getElementById('videoModal');
  var iframe = document.getElementById('videoModalIframe');

  if (!modal || !iframe) return;

  function openModal(videoId) {
    iframe.src = 'https://www.youtube.com/embed/' + videoId + '?autoplay=1&rel=0';
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    iframe.src = '';
    document.body.style.overflow = '';
  }

  document.querySelectorAll('[data-yt-id]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      openModal(link.getAttribute('data-yt-id'));
    });
  });

  document.querySelectorAll('[data-close]').forEach(function (el) {
    el.addEventListener('click', closeModal);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeModal();
  });
});

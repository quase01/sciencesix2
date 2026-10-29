(() => {
  'use strict';
  const dialog = document.getElementById('introScreen');
  const artwork = document.getElementById('introArtwork');
  const start = document.getElementById('introStart');

  artwork.addEventListener('error', () => {
    artwork.closest('.intro-art').classList.add('is-missing');
  });
  artwork.src = window.FireLabAssets?.['intro.png'] || 'intro.png';

  function open() {
    if (!dialog.open) dialog.showModal();
    document.body.classList.remove('intro-pending');
    document.body.classList.add('showing-intro');
    start.focus({ preventScroll: true });
  }

  function chooseCharacter() {
    if (!dialog.open) return;
    dialog.close();
    document.body.classList.remove('showing-intro');
    window.FireLabCharacter.open();
  }

  start.addEventListener('click', chooseCharacter);
  document.getElementById('introChoose').addEventListener('click', chooseCharacter);
  // Starting the adventure always goes through character selection.
  dialog.addEventListener('cancel', event => event.preventDefault());
  window.FireLabIntro = { open, isOpen: () => dialog.open };
})();

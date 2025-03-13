const themeSwitch = document.getElementById('theme-switch');

const enableDarkmode = () => {
  document.body.classList.add('darkmode')
  localStorage.setItem('darkmode', true)
};

const disableDarkmode = () => {
  document.body.classList.remove('darkmode')
  localStorage.setItem('darkmode', false)
};

const darkmode = localStorage.getItem('darkmode') === 'true';

if (darkmode) {
  enableDarkmode()
};

themeSwitch.addEventListener("click", () => {
  const darkmode = localStorage.getItem('darkmode') === 'true';
  if (darkmode) {
    disableDarkmode();
  } else {
    enableDarkmode();
  }
});
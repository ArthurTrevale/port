window.addEventListener('DOMContentLoaded', function() {
  var cinemasLink = document.getElementById('cinemas-link');
  var nenhumCinema = document.getElementById('nenhum-cinema');
  var counter = 0;
  var intervalId = null;
  var preventDefaultFlag = true; 
  if (cinemasLink && nenhumCinema) {
    cinemasLink.addEventListener('click', function(event) {
      nenhumCinema.classList.add('visible');
      nenhumCinema.textContent = 'Procurando cinemas próximos';
      counter = 0;

      intervalId = setInterval(function() {
        if (counter < 10) {
          nenhumCinema.textContent += '.';
          counter++;
        } else {
          clearInterval(intervalId);
          setTimeout(function() {
            preventDefaultFlag = false; 
            if (!preventDefaultFlag) {
              cinemasLink.click(); 
            }
          }, 500);
        }
      }, 100);
      
      if (preventDefaultFlag) {
        event.preventDefault(); 
      }
    });

    nenhumCinema.addEventListener('transitionend', function() {
      preventDefaultFlag = false; 
    });
  }
});

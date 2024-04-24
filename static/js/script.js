window.onload = function() {
  const cards = document.querySelectorAll('.card');
  let currentIndex = 0;

  function prevSlide() {
    currentIndex = (currentIndex === 0) ? cards.length - 1 : currentIndex - 1;
    showSlide(currentIndex);
  }

  function nextSlide() {
    currentIndex = (currentIndex === cards.length - 1) ? 0 : currentIndex + 1;
    showSlide(currentIndex);
  }

  function showSlide(index) {
    cards.forEach((card, i) => {
      if (i === index) {
        card.classList.add('active');
      } else {
        card.classList.remove('active');
      }
    });
  }

  document.querySelector('.prev').addEventListener('click', function() {
    prevSlide();
  });

  document.querySelector('.next').addEventListener('click', function() {
    nextSlide();
  });

  cards.forEach(card => {
    card.addEventListener('click', function() {
      card.classList.toggle('flipped');
    });
  });

  showSlide(currentIndex);
};
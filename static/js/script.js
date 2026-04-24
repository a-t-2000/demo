let currentSlide = 0;

function getSlides() {
    return document.querySelectorAll('.slide');
}

function showSlide(index) {
    let slides = getSlides();

    slides.forEach(slide => slide.classList.remove('active'));

    if (index >= slides.length) {
        currentSlide = 0;
    }

    if (index < 0) {
        currentSlide = slides.length - 1;
    }

    slides[currentSlide].classList.add('active');
}

function nextSlide() {
    currentSlide++;
    showSlide(currentSlide);
}

function prevSlide() {
    currentSlide--;
    showSlide(currentSlide);
}

setInterval(nextSlide, 3000);
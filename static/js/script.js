document.addEventListener('DOMContentLoaded', function () {
    const elements = document.querySelectorAll('.hidden');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fadeIn');
                observer.unobserve(entry.target);
            }
        });
    });

    elements.forEach(element => {
        observer.observe(element);
    });
});

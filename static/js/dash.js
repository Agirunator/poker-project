const boxes = document.querySelectorAll('.box');

boxes.forEach(box => {
    box.addEventListener('mouseenter', () => {
        boxes.forEach(otherBox => {
            if (otherBox !== box) {
                otherBox.style.width = '25vw';
        }
    });
    box.style.width = '35vw';
    });

    box.addEventListener('mouseleave', () => {
        boxes.forEach(otherBox => {
            otherBox.style.width = '30vw';
        });
    });
});

boxes.forEach(box => {
    box.addEventListener('click', () => {
        const url = box.getAttribute('data-href');
        
        window.location.href = url;
    });
});
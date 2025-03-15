const boxes = document.querySelectorAll('.box');

boxes.forEach(box => {
    box.addEventListener('mouseenter', () => {
        boxes.forEach(otherBox => {
            if (otherBox !== box) {
                otherBox.computedStyleMap.width = '25vw';
        }
    });
    box.computedStyleMap.width = '35vw';
    });

    box.addEventListener('mouseleave', () => {
        boxes.forEach(otherBox => {
            otherBox.computedStyleMap.width = '30vw';
        });
    });
});
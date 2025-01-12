document.querySelectorAll('.qtc-grid-item div[contenteditable]').forEach(div => {
    div.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault(); 
        }
    });
});

document.querySelectorAll('.qtc-grid-item div[contenteditable]').forEach(div => {
    div.addEventListener('input', (event) => {
        const target = event.target;
        target.style.height = 'auto'; 
        target.style.height = `${target.scrollHeight}px`;
    });
});
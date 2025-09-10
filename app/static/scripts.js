function paraphraseDescription(index) {
    const descriptionElement = document.querySelectorAll('.description')[index];
    const originalText = descriptionElement.innerText;

    // Simulate paraphrasing
    descriptionElement.innerText = "[Paraphrased] " + originalText;

    // Add a highlight effect
    descriptionElement.style.transition = "background-color 0.5s ease";
    descriptionElement.style.backgroundColor = "#dff0d8"; // Light green
    setTimeout(() => {
        descriptionElement.style.backgroundColor = "transparent";
    }, 1000);
}

document.getElementById('dark-mode-toggle').addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
});

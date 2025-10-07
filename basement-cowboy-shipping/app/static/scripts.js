// Centralized frontend script extracted from details.html
// Ensure axios sends cookies for same-origin requests so Flask session is preserved
if (window.axios) axios.defaults.withCredentials = true;

// Image preview modal (reusable)
(function () {
    const previewModalHtml = `
    <div class="modal fade" id="imagePreviewModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content">
                <div class="modal-body p-0 text-center">
                    <img id="image-preview-el" src="" alt="Preview" style="max-width:100%; height:auto;" />
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </div>`;
    document.body.insertAdjacentHTML('beforeend', previewModalHtml);
    if (window.bootstrap && bootstrap.Modal) window._bc_imagePreviewModal = new bootstrap.Modal(document.getElementById('imagePreviewModal'));
})();

function showSpinner(idx) {
    const el = document.getElementById(`spinner-${idx}`);
    if (el) el.classList.remove('d-none');
}

function hideSpinner(idx) {
    const el = document.getElementById(`spinner-${idx}`);
    if (el) el.classList.add('d-none');
}

// click-to-enlarge images
document.addEventListener('click', (e) => {
    const target = e.target;
    if (target && target.id && target.id.startsWith('article-image-')) {
        const src = target.src;
        const previewEl = document.getElementById('image-preview-el');
        if (previewEl) previewEl.src = src;
        if (window._bc_imagePreviewModal) window._bc_imagePreviewModal.show();
    }
});

// Go Back button functionality
document.addEventListener('DOMContentLoaded', () => {
    const goBack = document.getElementById("go-back");
    if (goBack) goBack.addEventListener("click", () => window.history.back());
});

function selectAllPublish() {
    const checkboxes = document.querySelectorAll("input[name^='publish-']");
    checkboxes.forEach(checkbox => checkbox.checked = true);
}

async function publishArticles() {
    try {
        const formData = new FormData(document.getElementById("article-details-form"));
        const response = await axios.post("/publish_article", formData);

        if (response.data.success) {
            alert("Articles published successfully!");
            window.location.href = response.data.post_url;
        } else {
            alert("Failed to publish articles: " + response.data.error);
        }
    } catch (error) {
        console.error("Error publishing articles:", error);
        alert("An error occurred while publishing articles.");
    }
}

// Toolbar helpers
function setToolbarStatus(text) {
    const el = document.getElementById('toolbar-status');
    if (el) el.textContent = text;
}

function setToolbarProgress(percent) {
    const bar = document.getElementById('toolbar-progress-bar');
    if (bar) bar.style.width = `${percent}%`;
}

async function generateSummaryAndImage(index) {
    const summaryInput = document.getElementById(`summary-${index}`);
    const imageInput = document.getElementById(`image-${index}`);
    const articleImage = document.getElementById(`article-image-${index}`);

    const errorDiv = document.getElementById('error-message');
    errorDiv.classList.add('d-none');
    errorDiv.textContent = '';

    try {
        setToolbarStatus('Starting: Generating summary...');
        setToolbarProgress(10);

        if (!summaryInput.value.trim()) {
            const summaryResponse = await axios.post('/ai_summarize', { link: document.getElementById(`link-${index}`).value });
            if (summaryResponse.data.success) {
                summaryInput.value = summaryResponse.data.summary;
            } else {
                errorDiv.textContent = 'Failed to generate summary: ' + (summaryResponse.data.error || 'Unknown error');
                errorDiv.classList.remove('d-none');
                setToolbarStatus('Error generating summary');
                setToolbarProgress(0);
                return;
            }
        }

        setToolbarStatus('Generating image...');
        setToolbarProgress(50);
        // prefer a saved custom prompt if the user edited one
        const savedPrompt = document.getElementById(`prompt-${index}`)?.value;
        const promptToUse = (savedPrompt && savedPrompt.length > 5) ? savedPrompt : summaryInput.value;
        showSpinner(index);
        const statusBadge = document.getElementById(`article-status-${index}`);
        if (statusBadge) { statusBadge.textContent = 'Generating'; statusBadge.className = 'badge bg-info'; }
        const imageResponse = await axios.post('/generate_image', { keywords: promptToUse });
        if (imageResponse.data.success) {
            if (imageResponse.data.image_url) {
                imageInput.value = imageResponse.data.image_url;
                articleImage.src = imageResponse.data.image_url;
            } else if (imageResponse.data.b64) {
                const dataUrl = 'data:image/jpeg;base64,' + imageResponse.data.b64;
                imageInput.value = dataUrl;
                articleImage.src = dataUrl;
            }
            setToolbarStatus('Done');
            setToolbarProgress(100);
            // reset after short delay
            setTimeout(() => { setToolbarStatus('Idle'); setToolbarProgress(0); }, 1200);
            if (statusBadge) { statusBadge.textContent = 'Done'; statusBadge.className = 'badge bg-success'; }
        } else {
            const msg = imageResponse.data.error || 'Unknown error';
            errorDiv.textContent = 'Failed to generate image: ' + msg;
            errorDiv.classList.remove('d-none');
            setToolbarStatus('Error generating image');
            setToolbarProgress(0);
            if (statusBadge) { statusBadge.textContent = 'Error'; statusBadge.className = 'badge bg-danger'; }
            // fetch last debug info if available
            try {
                const dbg = await axios.get('/last_debug_generate_image');
                console.error('Debug generate_image:', dbg.data.debug || dbg.data);
                alert('Server debug info: ' + JSON.stringify(dbg.data.debug || dbg.data).slice(0, 1000));
            } catch (e) {
                console.debug('No debug file available');
            }
        }
        hideSpinner(index);
    } catch (err) {
        errorDiv.textContent = 'Error: ' + (err.response?.data?.error || err.message || err);
        errorDiv.classList.remove('d-none');
        setToolbarStatus('Error');
        setToolbarProgress(0);
    }
}

async function generateSummary(index) {
    const summaryInput = document.getElementById(`summary-${index}`);
    const linkInput = document.getElementById(`link-${index}`);

    if (!linkInput.value.trim()) return;

    setToolbarStatus('Generating summary...');
    setToolbarProgress(10);

    try {
        const response = await axios.post('/ai_summarize', { link: linkInput.value });
        if (response.data.success) {
            summaryInput.value = response.data.summary;
            setToolbarProgress(100);
            setTimeout(() => { setToolbarStatus('Idle'); setToolbarProgress(0); }, 700);
        }
    } catch (error) {
        console.error('Error generating summary:', error);
        setToolbarStatus('Error generating summary');
        setToolbarProgress(0);
    }
}

async function generateAllSummaries() {
    // Only operate on summaries that have their select checkbox checked
    const selected = Array.from(document.querySelectorAll("input[id^='select-summary-']:checked"));
    if (selected.length === 0) {
        alert('No summaries selected. Please check the checkbox next to each summary you want to generate.');
        return;
    }

    let completed = 0;
    const total = selected.length;

    setToolbarStatus('Generating selected summaries...');
    setToolbarProgress(5);

    for (const chk of selected) {
        const index = chk.id.split('-')[2];
        await generateSummary(index);
        completed++;
        setToolbarProgress(Math.round((completed / total) * 100));
    }

    setToolbarStatus('Selected summaries complete');
    setTimeout(() => { setToolbarStatus('Idle'); setToolbarProgress(0); }, 800);
}

// Bulk generate images handler
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('generate-images')?.addEventListener('click', async () => {
        const selectedIndexes = [];
        document.querySelectorAll("input[name='generate-image']:checked").forEach(checkbox => {
            // checkbox id format: generate-image-<index>
            const parts = checkbox.id.split("-");
            selectedIndexes.push(parts[2]);
        });

        if (selectedIndexes.length === 0) {
            alert('No articles selected for image generation.');
            return;
        }

        if (!confirm(`Generate images for ${selectedIndexes.length} articles?`)) return;

        const errorDiv = document.getElementById('error-message');
        errorDiv.classList.add('d-none');
        errorDiv.textContent = '';

        setToolbarStatus('Generating images...');
        setToolbarProgress(10);

        let completed = 0;
        for (const index of selectedIndexes) {
            try {
                // skip if image already exists
                const imageInput = document.getElementById(`image-${index}`);
                if (imageInput && imageInput.value.trim()) {
                    completed++;
                    setToolbarProgress(Math.round((completed / selectedIndexes.length) * 100));
                    continue;
                }

                const summaryInput = document.getElementById(`summary-${index}`);
                const promptInput = document.getElementById(`prompt-${index}`);
                const articleImage = document.getElementById(`article-image-${index}`);

                // use custom prompt if available and long enough
                const savedPrompt = promptInput?.value;
                const promptToUse = (savedPrompt && savedPrompt.length > 5) ? savedPrompt : summaryInput.value;

                showSpinner(index);
                const statusBadge = document.getElementById(`article-status-${index}`);
                if (statusBadge) { statusBadge.textContent = 'Generating'; statusBadge.className = 'badge bg-info'; }
                const imageResponse = await axios.post('/generate_image', { keywords: promptToUse });
                if (imageResponse.data.success) {
                    if (imageResponse.data.image_url) {
                        imageInput.value = imageResponse.data.image_url;
                        articleImage.src = imageResponse.data.image_url;
                    } else if (imageResponse.data.b64) {
                        const dataUrl = 'data:image/jpeg;base64,' + imageResponse.data.b64;
                        imageInput.value = dataUrl;
                        articleImage.src = dataUrl;
                    }
                    if (statusBadge) { statusBadge.textContent = 'Done'; statusBadge.className = 'badge bg-success'; }
                } else {
                    const msg = imageResponse.data.error || 'Unknown error';
                    errorDiv.textContent = 'Failed to generate image: ' + msg;
                    errorDiv.classList.remove('d-none');
                    if (statusBadge) { statusBadge.textContent = 'Error'; statusBadge.className = 'badge bg-danger'; }
                    // fetch last debug info if available
                    try {
                        const dbg = await axios.get('/last_debug_generate_image');
                        console.error('Debug generate_image:', dbg.data.debug || dbg.data);
                        alert('Server debug info: ' + JSON.stringify(dbg.data.debug || dbg.data).slice(0, 1000));
                    } catch (e) {
                        console.debug('No debug file available');
                    }
                }
            } catch (err) {
                errorDiv.textContent = 'Error: ' + (err.response?.data?.error || err.message || err);
                errorDiv.classList.remove('d-none');
            }
            completed++;
            setToolbarProgress(Math.round((completed / selectedIndexes.length) * 100));
        }

        setToolbarStatus('Image generation complete');
        setTimeout(() => { setToolbarStatus('Idle'); setToolbarProgress(0); }, 800);
    });
});

document.getElementById('dark-mode-toggle').addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
});

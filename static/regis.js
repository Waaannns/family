function showPopup(success, message) {
    const modal = document.getElementById("modal");
    const modalContent = document.getElementById("modal-content");

    if (success) {
        modalContent.innerHTML = `
            <div class="icon">&#10004;</div>
            <h2>Success</h2>
            <p>${message}</p>
        `;
    } else {
        modalContent.innerHTML = `
            <div class="icon" style="color: red;">&#10006;</div>
            <h2>Failed</h2>
            <p>${message}</p>
        `;
    }

    modal.style.display = "flex";

    setTimeout(() => {
        modal.style.display = "none";
    }, 5000);
}

function handleSubmit(event) {
    event.preventDefault();

    const formData = new FormData(document.getElementById("dataForm"));

    fetch('/add', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        showPopup(data.success, data.message);
        if (data.success) {
            setTimeout(() => {
                window.location.href = '/otp';
            }, 5000);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showPopup(false, 'Terjadi kesalahan pada server');
    });
}
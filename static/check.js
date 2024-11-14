function showPopup(success, message) {
    const modal = document.getElementById("modal");
    const modalContent = document.getElementById("modal-content");
    modalContent.innerHTML = success ? `
        <div class="icon" style="color: green;">&#10004;</div>
        <h2>Success</h2>
        <p>${message}</p>
    ` : `
        <div class="icon" style="color: red;">&#10006;</div>
        <h2>Failed</h2>
        <p>${message}</p>
    `;
    modal.style.display = "flex";
    setTimeout(() => modal.style.display = "none", 5000);
}

function updateTable(data) {
    const table = document.querySelector("table");
    let rows = `
        <tr>
            <th>Nama Kupon</th>
            <th>Jumlah Kupon</th>
        </tr>
    `;
    data.forEach(item => {
        rows += `<tr><td>${item.nama}</td><td>${item.jumlah}</td></tr>`;
    });
    table.innerHTML = rows;
}

function handleSubmit(event) {
    event.preventDefault();
    const formData = new FormData(document.getElementById("dataForm"));
    fetch('/kupon', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        showPopup(data.success, data.message);
        if (data.success && data.data) {
            updateTable(data.data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showPopup(false, 'Terjadi kesalahan pada server');
    });
}
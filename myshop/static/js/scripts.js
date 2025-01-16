function showMessage(typeMessage) {
    const messageContent = document.querySelector("#message-content");
    messageContent.innerHTML = "";
    const alertDiv = document.createElement("div");
    alertDiv.role = "alert";
    if (typeMessage) {
        alertDiv.className = `alert alert-success`;
        alertDiv.textContent = "Товар успешно добавлен в корзину!";
    } else {
        alertDiv.className = `alert alert-danger`;
        alertDiv.textContent = "Произошла ошибка при добавлении товара.!";
    }
    messageContent.appendChild(alertDiv);
    const messageModal = new bootstrap.Modal(
        document.getElementById("messageModal")
    );
    messageModal.show();
}

document.addEventListener("DOMContentLoaded", function () {
    const cartForms = document.querySelectorAll(".add-to-cart-form");

    cartForms.forEach((form) => {
        form.addEventListener("submit", function (event) {
            event.preventDefault(); // Предотвращаем отправку формы

            const url = form.action; // URL для отправки запроса
            const formData = new FormData(form);

            fetch(url, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        document.querySelector("#cart-total").textContent =
                            data.cart_total;
                        showMessage(true);
                    } else {
                        showMessage(false);
                    }
                })
                .catch((error) => {
                    console.error("Ошибка:", error);
                    alert("Произошла ошибка при добавлении товара.");
                    showMessage(false);
                });
        });
    });
});

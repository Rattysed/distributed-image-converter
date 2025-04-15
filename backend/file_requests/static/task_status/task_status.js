document.addEventListener("DOMContentLoaded", () => {
    const statusMessage = document.getElementById("status-message");
    const resultContainer = document.getElementById("result-container");
    const requestId = document.getElementById("request-id").value;

    const checkStatus = async () => {
        try {
            const response = await fetch(`/check-status/${requestId}/`, {
                method: "GET",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            if (response.ok) {
                const data = await response.json();

                if (data.status === "pending") {
                    statusMessage.textContent = "Ожидайте, задача выполняется...";
                } else if (data.status === "error") {
                    statusMessage.textContent = "Произошла ошибка. Перенаправление на главную страницу...";
                    clearInterval(intervalId);
                    setTimeout(() => {
                        window.location.href = "/";
                    }, 3000);
                } else if (data.status === "ready") {
                    statusMessage.textContent = "Задача завершена!";
                    resultContainer.innerHTML = `<a href="${data.link}" target="_blank">Скачать результат</a>`;
                    clearInterval(intervalId); // Останавливаем запросы
                }
            } else {
                console.error("Ошибка запроса к серверу", response.statusText);
            }
        } catch (error) {
            console.error("Ошибка при выполнении запроса", error);
        }
    };

    const intervalId = setInterval(checkStatus, 3000);
});

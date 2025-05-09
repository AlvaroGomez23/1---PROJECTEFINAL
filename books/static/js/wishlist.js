document.addEventListener("DOMContentLoaded", function () {
    const wishlistButtons = document.querySelectorAll(".wishlist-btn");

    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    
    function updateButtonState(button, inWishlist) {
        if (inWishlist === "true") {
            button.textContent = "Eliminar de la llista de desitjats";
        } else {
            button.textContent = "Afegir a llista de desitjats";
        }
        button.setAttribute("data-in-wishlist", inWishlist);
    }

    
    wishlistButtons.forEach((button) => {
        const inWishlist = button.getAttribute("data-in-wishlist");
        updateButtonState(button, inWishlist);

        button.addEventListener("click", function () {
            const bookId = this.dataset.bookId;
            const currentState = this.getAttribute("data-in-wishlist");
            const newState = currentState === "true" ? "false" : "true";

            fetch(toggleWishlistUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({ book_id: bookId }),
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.status === "added") {
                        updateButtonState(this, "true");
                    } else if (data.status === "removed") {
                        updateButtonState(this, "false");
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    alert("Hi ha hagut un error. Torna-ho a intentar.");
                });
        });
    });
});
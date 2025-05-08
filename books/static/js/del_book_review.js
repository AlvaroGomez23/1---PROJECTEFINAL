document.addEventListener("DOMContentLoaded", function () {
    const deleteReviewModal = document.getElementById("deleteReviewModal");
    if (deleteReviewModal) {
        deleteReviewModal.addEventListener("show.bs.modal", function (event) {
            const button = event.relatedTarget;
            const reviewId = button.getAttribute("data-review-id");
            const deleteReviewForm = document.getElementById("deleteReviewForm");
            const originalAction = deleteReviewForm.getAttribute("action");
            const newAction = originalAction.replace(/\/\d+\/$/, `/${reviewId}/`);
            deleteReviewForm.setAttribute("action", newAction);
        });
    }
});

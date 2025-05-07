document.addEventListener("DOMContentLoaded", function () {
    const deleteReviewModal = document.getElementById("deleteReviewModal");
    if (deleteReviewModal) {
        deleteReviewModal.addEventListener("show.bs.modal", function (event) {
            const button = event.relatedTarget;
            const reviewId = button.getAttribute("data-review-id");

            const modalReviewId = document.getElementById("modalReviewId");
            modalReviewId.textContent = reviewId;

            const deleteReviewForm = document.getElementById("deleteReviewForm");
            const newAction = `/users/delete_review_user/${reviewId}`;
            deleteReviewForm.setAttribute("action", newAction);
        });
    }
});

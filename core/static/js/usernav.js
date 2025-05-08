document.addEventListener('DOMContentLoaded', function () {
    const dropdownTrigger = document.querySelector('.nav-compte');
    const dropdown = new bootstrap.Dropdown(dropdownTrigger);
    const dropdownWrapper = dropdownTrigger.closest('.dropdown');

    dropdownTrigger.addEventListener('focus', () => {
      dropdown.show();
    });

    dropdownWrapper.addEventListener('focusout', () => {
      setTimeout(() => {
        if (!dropdownWrapper.contains(document.activeElement)) {
          dropdown.hide();
        }
      }, 100);
    });

    dropdownWrapper.addEventListener('mouseenter', () => dropdown.show());
    dropdownWrapper.addEventListener('mouseleave', () => dropdown.hide());
  });
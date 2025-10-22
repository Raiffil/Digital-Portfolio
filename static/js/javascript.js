// Portfolio filter toggle
document.addEventListener('DOMContentLoaded', () => {
  const filterBtn = document.getElementById('filter-btn');
  const filterColumn = document.getElementById('filter-column');

  if (filterBtn && filterColumn) {
    filterBtn.addEventListener('click', () => {
      filterColumn.classList.toggle('show');
    });
  }
});

document.addEventListener("DOMContentLoaded", () => {
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.nav-link');
  
    sidebarLinks.forEach(link => {
      if (currentPath.includes(link.getAttribute('href'))) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  });
  
// Posts Style

// Research Group Presentation (Full Horizontal)
var presentation_area = document.querySelector(".section .container .columns .column");
presentation_area.classList.remove("is-8");
presentation_area.classList.add("is-12");

// Latest Posts (Full Horizontal, x3 Multiline)
var posts_area = document.querySelectorAll(".section .container .columns .column")[1];
posts_area.classList.remove("is-4-desktop");
posts_area.classList.remove("is-4-tablet");
var posts = posts_area.querySelectorAll(".columns .column");
posts.forEach((post) => {
    post.classList.remove("is-12");
    post.classList.add('is-4');
  });
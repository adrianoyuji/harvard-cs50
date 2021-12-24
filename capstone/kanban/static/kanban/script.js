document.addEventListener("DOMContentLoaded", handle_mainscript_pageload);

function handle_mainscript_pageload() {
  handle_navbar_active();
}

function handle_navbar_active() {
  const pathname = window.location.pathname;
  if (pathname === "/") {
    document
      .querySelector("#home-anchor")
      .setAttribute("class", "nav-link active");
    return;
  }
  if (pathname.includes("/boards")) {
    document
      .querySelector("#boards-anchor")
      .setAttribute("class", "nav-link active");
    return;
  }
  if (pathname.includes("/board/")) {
    document
      .querySelector("#boards-anchor")
      .setAttribute("class", "nav-link active");
    return;
  }
  if (pathname.includes("/notifications")) {
    document
      .querySelector("#notifications-anchor")
      .setAttribute("class", "nav-link active");
    return;
  }
  if (pathname.includes("/login")) {
    document
      .querySelector("#login-anchor")
      .setAttribute("class", "nav-link active");
    return;
  }
  if (pathname.includes("/register")) {
    document
      .querySelector("#register-anchor")
      .setAttribute("class", "nav-link active");
    return;
  }
}

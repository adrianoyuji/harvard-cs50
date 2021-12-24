document.addEventListener("DOMContentLoaded", handle_notifications_page);

function handle_notifications_page() {
  const pathname = window.location.pathname;
  if (pathname === "/notifications") {
    fetch_notifications();
    document
      .querySelector("#update-notifications")
      .addEventListener("click", fetch_notifications);
  }
}

function clearNodes() {
  document.querySelector("#paginator").innerHTML = "";
  document.querySelector("#notifications-list").innerHTML = "";
}

function fetch_notifications() {
  clearNodes();
  const params = Object.fromEntries(
    new URLSearchParams(window.location.search).entries()
  );
  const nodeList = document.querySelector("#notifications-list");
  fetch(`/api/notifications?${params.page ? `page=${params.page}` : ""}`, {
    method: "GET",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("An Error occurred...");
      }
    })
    .then(({ notifications, pagination }) => {
      notifications.forEach((notification) => {
        let notificationItem = document.createElement("a");
        notificationItem.setAttribute(
          "class",
          "list-group-item d-flex flex-row"
        );
        notificationItem.setAttribute(
          "href",
          `/board/${notification.board.id}`
        );
        notificationItem.innerHTML = `<span class="flex-grow-1">${notification.message}</span><small class='text-muted'>At ${notification.timestamp}</small>`;
        nodeList.appendChild(notificationItem);
      });
      createPagination(pagination, "/notifications");
    })

    .catch((error) => console.log(error));
}

function createPagination(pagination, url) {
  const paginationNode = document.querySelector("#paginator");
  let previousItem = document.createElement("li");
  let nextItem = document.createElement("li");
  previousItem.setAttribute(
    "class",
    `page-item ${pagination.has_previous ? "" : "disabled"}`
  );
  nextItem.setAttribute(
    "class",
    `page-item ${pagination.has_next ? "" : "disabled"}`
  );

  if (pagination.has_previous) {
    previousItem.innerHTML = `<a class="page-link" href="${url}?page=${
      pagination.current_page - 1
    }">&laquo;</a>`;
  } else {
    previousItem.innerHTML = '<span class="page-link">&laquo;</span>';
  }

  if (pagination.has_next) {
    nextItem.innerHTML = `<a class="page-link" href="${url}?page=${
      pagination.current_page + 1
    }">&raquo;</a>`;
  } else {
    nextItem.innerHTML = '<span class="page-link">&raquo;</span>';
  }

  paginationNode.append(previousItem);
  pagination.page_range.forEach((page) => {
    let listItem = document.createElement("li");
    if (page !== pagination.current_page) {
      listItem.setAttribute("class", "page-item");
      listItem.innerHTML = `<a class="page-link" href="${url}?page=${page}">${page}</a>`;
    } else {
      listItem.setAttribute("class", "page-item active");
      listItem.innerHTML = `<span class="page-link">${page}</span>`;
    }
    paginationNode.append(listItem);
  });
  paginationNode.append(nextItem);
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

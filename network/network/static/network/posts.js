document.addEventListener("DOMContentLoaded", () => handle_pageload());

function handle_pageload() {
  const pathname = window.location.pathname;
  const user_id = !!document.getElementById("user_id")
    ? JSON.parse(document.getElementById("user_id").textContent)
    : undefined;
  const urlSearchParams = new URLSearchParams(window.location.search);
  const params = Object.fromEntries(urlSearchParams.entries());

  if (pathname === "/") {
    const node = document.querySelector("#create-post");
    if (!!node) node.addEventListener("submit", new_post);
    load_posts({
      params,
      user_id,
      currentPage: pathname,
      request_url: "/posts",
    });
  }

  if (pathname === "/following") {
    document.querySelector("#create-post").addEventListener("submit", new_post);
    load_posts({
      params,
      user_id,
      currentPage: pathname,
      request_url: "/following-posts",
    });
  }
  if (pathname.includes("/user/")) {
    const idArray = pathname.split("/");
    load_posts({
      params,
      user_id,
      currentPage: pathname,
      request_url: `/user/posts/${idArray[2]}`,
    });
  }
}

function new_post(e) {
  e.preventDefault();
  const message = document.querySelector("#post-message").value;
  const csrftoken = document.getElementsByName("csrfmiddlewaretoken");
  fetch("/posts", {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": csrftoken[0].value,
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
    }),
  })
    .then((response) => response.json())
    .then((result) => {
      document.querySelector("#posts-list").innerHTML = ""; // resets div's content
      document.querySelector("#post-message").value = ""; //clears textarea
      document.querySelector("#paginator").innerHTML = ""; //clears pagination
      handle_pageload();
    });
}

function load_posts({ params, user_id = 0, currentPage, request_url }) {
  fetch(`${request_url}?${params.page ? `page=${params.page}` : ""}`)
    .then((response) => response.json())
    .then((response) => {
      response.posts.forEach((post) => {
        let postDiv = document.createElement("div");

        postDiv.setAttribute("class", "post-container");

        postDiv.innerHTML = `
          <div class='post-username'>
            <span><a class='username-anchor' href="/user/${post.owner.id}">${
          post.owner.username
        }</a></span>
          </div>      
          <div class='post-data'>
            <div id='post-message-${post.id}'><p id='post-paragraph-${
          post.id
        }' class='post-message'>${post.message}</p></div>
            ${
              user_id === post.owner.id
                ? `<span class='edit-button' id='edit-${post.id}'>Edit</span>`
                : ""
            }
            <span><b id='qnt-likes-${post.id}'>${
          post.likes_count
        }</b> likes</span>
            ${
              !!user_id
                ? post.liked
                  ? `<span class='edit-button' id='like-${post.id}'>Liked</span>`
                  : `<span class='edit-button' id='like-${post.id}'>Like</span>`
                : ""
            }
            <span class='post-date'>${post.timestamp}</span>
          </div>
        `;
        document.querySelector("#posts-list").appendChild(postDiv);
        user_id &&
          document
            .querySelector(`#like-${post.id}`)
            .addEventListener("click", () => handle_like(post.id));
        user_id === post.owner.id &&
          document
            .querySelector(`#edit-${post.id}`)
            .addEventListener("click", () => {
              let editBtnNode = document.querySelector(`#edit-${post.id}`);
              editBtnNode.innerHTML = "";
              let messageValue = document.querySelector(
                `#post-paragraph-${post.id}`
              ).innerHTML;
              let editNode = document.querySelector(`#post-message-${post.id}`);
              editNode.innerHTML = `<textarea
              name="message"
              required
              rows="5"
              cols="33"
              id="edit-textarea-${post.id}"
              style="width:100%;"
            >${messageValue}</textarea>
            <input type="button" id="submit-${post.id}" value="Edit Post" class="btn btn-primary btn-sm" />`;
              document
                .querySelector(`#submit-${post.id}`)
                .addEventListener("click", () =>
                  handle_edit_post(post.id, user_id)
                );
            });
      });

      createPagination(response.pagination, currentPage);
    });
}

function handle_edit_post(post_id, user_id) {
  let messageValue = document.querySelector(`#edit-textarea-${post_id}`).value;

  fetch(`/post/${post_id}`, {
    method: "PUT",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_id: user_id,
      post_id: post_id,
      message: messageValue,
    }),
  })
    .then((response) => response.json())
    .then((response) => {
      let editNode = document.querySelector(`#post-message-${post_id}`);
      editNode.innerHTML = `<p class='post-message' id='post-paragraph-${post_id}'>${messageValue}</p>`;
      let editBtnNode = document.querySelector(`#edit-${post_id}`);
      editBtnNode.innerHTML = "Edit";
    })
    .catch((error) => {});
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
    }">Previous</a>`;
  } else {
    previousItem.innerHTML = '<span class="page-link">Previous</span>';
  }

  if (pagination.has_next) {
    nextItem.innerHTML = `<a class="page-link" href="${url}?page=${
      pagination.current_page + 1
    }">Next</a>`;
  } else {
    nextItem.innerHTML = '<span class="page-link">Next</span>';
  }

  paginationNode.append(previousItem);
  pagination.page_range.forEach((page) => {
    let listItem = document.createElement("li");
    if (page !== pagination.current_page) {
      listItem.setAttribute("class", "page-item");
      listItem.innerHTML = `<a class="page-link" href="${url}?page=${page}">${page}</a>`;
    } else {
      listItem.setAttribute("class", "page-item active");
      listItem.innerHTML = `<span class="page-link">${page}<span class="sr-only">(current)</span></span>`;
    }
    paginationNode.append(listItem);
  });
  paginationNode.append(nextItem);
}

function handle_like(post_id) {
  fetch(`/like/${post_id}`, {
    method: "PUT",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((response) => {
      let likedNode = document.querySelector(`#like-${post_id}`);
      likedNode.innerHTML = response.status;
      let likesQuantityNode = document.querySelector(`#qnt-likes-${post_id}`);
      likesQuantityNode.innerHTML = response.likes_count;
    })
    .catch((error) => {});
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

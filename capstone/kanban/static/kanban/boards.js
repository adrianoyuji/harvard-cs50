document.addEventListener("DOMContentLoaded", handle_boards_pageload);

function handle_boards_pageload() {
  const pathname = window.location.pathname;
  if (pathname === "/boards") {
    load_boards();
    document
      .querySelector("#submit-board")
      .addEventListener("click", handle_new_board);
  }
}

function load_boards() {
  document.querySelector("#board-list").innerHTML = "";
  fetch("/api/boards", {
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
        throw new Error("An Error occurred.");
      }
    })
    .then(({ boards }) => {
      boards.forEach((board, index) => {
        let boardDiv = document.createElement("li");
        boardDiv.setAttribute("class", "list-group-item d-flex flex-column");
        boardDiv.innerHTML = `<span>
                                <strong>${board.title}</strong>
                              </span>
                              <span>
                                <small>${board.description}</small>
                              </span>
                              <span>
                                <small class='text-muted'>Created at ${board.timestamp}</small>
                              </span>
                              <div class='d-flex flex-row mt-3'>
                                <a href='/board/${board.id}' type="button" class="btn btn-primary btn-sm me-3">View</a>
                                <button id='edit-board-${board.id}' type="button" class="btn btn-secondary btn-sm me-3">Edit</button>
                                <button id='delete-board-${board.id}' type="button" class="btn btn-danger btn-sm">Delete</button>
                              </div>`;
        document.querySelector("#board-list").appendChild(boardDiv);
        document
          .querySelector(`#edit-board-${board.id}`)
          .addEventListener("click", () => open_edit_modal(board));
        document
          .querySelector(`#delete-board-${board.id}`)
          .addEventListener("click", () => handle_delete_board(board));
      });
    })
    .catch((error) => {
      console.log(error);
    });
}

function handle_delete_board(board) {
  const decision = window.confirm(
    `Are you sure you want to delete ${board.title}?`
  );
  if (decision) {
    fetch(`/api/boards/${board.id}`, {
      method: "DELETE",
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
          throw new Error("An Error occurred.");
        }
      })
      .then((response) => {
        load_boards();
      })
      .catch((error) => window.alert(error.message));
  }
}

function handle_new_board() {
  const title = document.querySelector("#board-title").value;
  const description = document.querySelector("#board-description").value;

  const csrftoken = document.getElementsByName("csrfmiddlewaretoken");
  fetch("/api/boards", {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": csrftoken[0].value,
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      title,
      description,
    }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("An Error occurred.");
      }
    })
    .then((response) => {
      document.querySelector("#board-title").value = "";
      document.querySelector("#board-description").value = "";
      document.querySelector("#close-modal-button").click();
      load_boards();
    })
    .catch((error) => {
      console.log(error);
    });
}

function open_edit_modal(board) {
  document.querySelector("#edit-board-button").click();
  document.querySelector("#edit-board-title").value = board.title;
  document.querySelector("#edit-board-description").value = board.description;
  document
    .querySelector("#edit-submit-board")
    .addEventListener("click", () => handle_edit_board(board));
}

function handle_edit_board(board) {
  const title = document.querySelector("#edit-board-title").value;
  const description = document.querySelector("#edit-board-description").value;

  const csrftoken = document.getElementsByName("csrfmiddlewaretoken");
  fetch(`/api/boards/${board.id}`, {
    method: "PUT",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": csrftoken[0].value,
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      title,
      description,
    }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("An Error occurred.");
      }
    })
    .then((response) => {
      document.querySelector("#edit-board-title").value = "";
      document.querySelector("#edit-board-description").value = "";
      document.querySelector("#close-edit-modal-button").click();
      load_boards();
    })
    .catch((error) => {
      console.log(error);
    });
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

let user_list = [];
const validParentNodes = [
  "todo-body",
  "backlog-body",
  "inprogress-body",
  "closed-body",
  "done-body",
];
const validStatus = ["backlog", "todo", "inprogress", "done", "closed"];
document.addEventListener("DOMContentLoaded", handle_board_pageload);

function handle_board_pageload() {
  const pathname = window.location.pathname;
  if (pathname.includes("/board/")) {
    const queryId = pathname.split("/");
    load_board({ board_id: queryId[2] });
  }
}

function load_board({ board_id }) {
  fetch(`/api/boards/${board_id}`, {
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
    .then(({ board }) => {
      document
        .querySelector("#submit-invite")
        .addEventListener("click", () => invite_user({ board_id: board.id }));

      user_list = [board.owner, ...board.allowed_users];
      document.querySelector("#backlog-button").addEventListener("click", () =>
        open_modal({
          status: "backlog",
          title: "Backlog",
          board_id: board_id,
        })
      );
      document.querySelector("#todo-button").addEventListener("click", () =>
        open_modal({
          status: "todo",
          title: "To do",
          board_id: board_id,
        })
      );
      document
        .querySelector("#inprogress-button")
        .addEventListener("click", () =>
          open_modal({
            status: "inprogress",
            title: "In Progress",
            board_id: board_id,
          })
        );
      document.querySelector("#done-button").addEventListener("click", () =>
        open_modal({
          status: "done",
          title: "Done",
          board_id: board_id,
        })
      );

      board.tasks.forEach((task) => {
        render_task_card(task);
      });
      document.querySelector("#board-title").innerHTML = board.title;
      let invitedContainer = document.querySelector("#invited-container");
      user_list.forEach((user, index) => {
        let userNode = document.createElement("span");
        userNode.setAttribute(
          "class",
          "d-flex flex-row my-1 align-items-center"
        );
        userNode.setAttribute("id", user.username);
        userNode.innerHTML = `<strong class='flex-grow-1'>${
          user.username
        }</strong>${
          index === 0
            ? "<strong>Owner</strong>"
            : `<button class='btn btn-danger btn-sm' id='remove-${user.username}'>Remove</button>`
        }`;
        invitedContainer.appendChild(userNode);
        index !== 0 &&
          document
            .getElementById(`remove-${user.username}`)
            .addEventListener("click", () =>
              delete_invited_user({
                board_id: board.id,
                username: user.username,
              })
            );
      });
    })
    .catch((error) => {
      console.log(error);
    });
}

function render_task_card(task) {
  let taskDiv = document.createElement("div");
  taskDiv.setAttribute("style", "18rem");
  taskDiv.setAttribute("id", `${task.id}`);
  taskDiv.setAttribute("draggable", "true");
  taskDiv.setAttribute("ondragstart", "dragstart_handler(event);");
  taskDiv.setAttribute("ondrop", "drop_on_card(event)");
  taskDiv.innerHTML = `<div class="card-body">
    ${task.title ? `<h5 class="modal-title">${task.title}</h5>` : ""}
    ${
      task.description ? `<p class="card-text m-0">${task.description}</p>` : ""
    }
    <div><small><strong>Assignee: </strong><span>${
      task.assignee ? task.assignee.username : "None"
    }</span></small></div>
    <div><small><strong>Reviewer: </strong><span>${
      task.reviewer ? task.reviewer.username : "None"
    }</span></small></div>
    <div>
      <small>${task.timestamp}</small>
    </div>
    <div class="d-grid gap-2 d-md-flex justify-content-md-end">
      <button id='edit-${
        task.id
      }' class="btn btn-sm btn-outline-light" type="button">Edit</button>
    </div>
  </div> 
 `;

  let container = null;
  switch (task.status) {
    case "todo":
      taskDiv.setAttribute("class", "card mb-3 text-white bg-primary");
      container = document.querySelector("#todo-body");
      container.insertBefore(taskDiv, container.firstChild);
      break;
    case "backlog":
      taskDiv.setAttribute("class", "card mb-3 text-white bg-secondary");
      container = document.querySelector("#backlog-body");
      container.insertBefore(taskDiv, container.firstChild);
      break;
    case "inprogress":
      taskDiv.setAttribute("class", "card mb-3 text-dark bg-warning ");
      container = document.querySelector("#inprogress-body");
      container.insertBefore(taskDiv, container.firstChild);
      break;
    case "done":
      taskDiv.setAttribute("class", "card mb-3 text-white bg-success");
      container = document.querySelector("#done-body");
      container.insertBefore(taskDiv, container.firstChild);
      break;
    case "closed":
      taskDiv.setAttribute("class", "card mb-3 text-white bg-dark");
      container = document.querySelector("#closed-body");
      container.insertBefore(taskDiv, container.firstChild);
      break;
    default:
      taskDiv.setAttribute("class", "card mb-3 text-white bg-dark");
      container = document.querySelector("#closed-body");
      container.insertBefore(taskDiv, container.firstChild);
      break;
  }
  const editButton = document.querySelector(`#edit-${task.id}`);
  editButton.content = {
    task,
  };
  editButton.addEventListener("click", edit_modal);
}

function edit_modal(evt) {
  const { task } = evt.target.content;

  let assigneeSelect = document.querySelector("#edit-task-assignee");
  let reviewerSelect = document.querySelector("#edit-task-reviewer");
  assigneeSelect.innerHTML = `<option ${
    task.assignee ? "" : "selected"
  } value='0'>None</option>`;
  reviewerSelect.innerHTML = `<option ${
    task.assignee ? "" : "selected"
  } value='0'>None</option>`;
  user_list.forEach((user) => {
    let optionNode = document.createElement("option");
    optionNode.setAttribute("value", user.id);
    if (task.assignee && task.assignee.id == user.id)
      optionNode.setAttribute("selected", "true");
    optionNode.innerHTML = user.username;
    assigneeSelect.appendChild(optionNode);
    let optionNode2 = document.createElement("option");
    optionNode2.setAttribute("value", user.id);
    if (task.reviewer && task.reviewer.id == user.id)
      optionNode2.setAttribute("selected", "true");
    optionNode2.innerHTML = user.username;
    reviewerSelect.appendChild(optionNode2);
  });

  document.querySelector("#edit-task-title").value = task.title;
  document.querySelector("#edit-task-description").value = task.description;
  assigneeSelect.value = task.assignee ? task.assignee.id : 0;
  reviewerSelect.value = task.reviewer ? task.reviewer.id : 0;

  document.getElementById("task-status").value = task.status;

  const saveButton = document.querySelector("#submit-edit-task");
  saveButton.task = task;
  saveButton.addEventListener("click", update_task);
  document.querySelector("#edit-task-modal-button").click();
  const deleteButton = document.querySelector("#delete-task");
  deleteButton.task_id = task.id;
  deleteButton.addEventListener("click", delete_task);
}

function update_task(evt) {
  evt.preventDefault();
  const task = evt.target.task;
  const title = document.querySelector("#edit-task-title").value;
  if (!title) {
    window.alert("Task title is required!");
    return;
  }
  const description = document.querySelector("#edit-task-description").value;
  const assignee_id = document.querySelector("#edit-task-assignee").value;
  const reviewer_id = document.querySelector("#edit-task-reviewer").value;
  const status = document.getElementById("task-status").value;
  const csrftoken = document.getElementsByName("csrfmiddlewaretoken");
  fetch(`/api/task/${task.id}`, {
    method: "PUT",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": csrftoken[0].value,
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      description,
      assignee_id,
      reviewer_id,
      status,
      title,
    }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("An Error occurred...");
      }
    })
    .then((response) => {
      const oldTask = document.getElementById(task.id);
      oldTask.parentNode.removeChild(oldTask);
      render_task_card(response.task);
      document.querySelector("#close-edit-modal-button").click();
    })
    .catch((error) => console.log(error));
}

function open_modal({ status, title, board_id }) {
  document.querySelector("#task-title").value = "";
  document.querySelector("#task-description").value = "";
  document.querySelector("#task-assignee").value = 0;
  document.querySelector("#task-reviewer").value = 0;
  document.querySelector("#new-task").innerHTML = `New ${title} Task`;
  let assigneeSelect = document.querySelector("#task-assignee");
  let reviewerSelect = document.querySelector("#task-reviewer");
  assigneeSelect.innerHTML = "<option selected value='0'>None</option>";
  reviewerSelect.innerHTML = "<option selected value='0'>None</option>";
  user_list.forEach((user) => {
    let optionNode = document.createElement("option");
    optionNode.setAttribute("value", user.id);
    optionNode.innerHTML = user.username;
    assigneeSelect.appendChild(optionNode);
    let optionNode2 = document.createElement("option");
    optionNode2.setAttribute("value", user.id);
    optionNode2.innerHTML = user.username;
    reviewerSelect.appendChild(optionNode2);
  });

  const submitButton = document.querySelector("#submit-task");
  submitButton.status = status;
  submitButton.board_id = board_id;
  submitButton.addEventListener("click", create_task);

  document.querySelector("#task-modal-button").click();
}

function create_task(evt) {
  const board_id = evt.currentTarget.board_id;
  const status = evt.currentTarget.status;
  if (!validStatus.includes(status)) return;
  const description = document.querySelector("#task-description").value;
  const assignee_id = document.querySelector("#task-assignee").value;
  const reviewer_id = document.querySelector("#task-reviewer").value;
  const title = document.querySelector("#task-title").value;
  if (!title) {
    window.alert("Task title is required!");
    return;
  }
  const csrftoken = document.getElementsByName("csrfmiddlewaretoken");
  fetch(`/api/board/${board_id}/task`, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": csrftoken[0].value,
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      reviewer_id,
      description,
      assignee_id,
      status,
      title,
    }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("An Error occurred...");
      }
    })
    .then(({ task }) => {
      render_task_card(task);
      document.querySelector("#close-modal-button").click();
    })
    .catch((error) => console.log(error));
}

function dragstart_handler(ev) {
  const columnId = ev.target.id;
  ev.dataTransfer.setData("text/plain", columnId);
}

function allowDrop(event) {
  event.preventDefault();
}

function delete_task(event) {
  const id = event.target.task_id;
  const decision = window.confirm(`Are you sure you want to delete this task?`);
  if (decision) {
    fetch(`/api/task/${id}`, {
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
          throw new Error("An Error occurred...");
        }
      })
      .then((response) => {
        let taskNode = document.getElementById(id);
        taskNode.parentNode.removeChild(taskNode);
        document.querySelector("#close-edit-modal-button").click();
      })
      .catch((error) => window.alert(error.message));
  }
}

function drop_on_card(event) {
  let currentNode = event.target;
  let counter = 0;
  while (
    !validParentNodes.some((node) =>
      currentNode.parentNode.id
        ? node.includes(currentNode.parentNode.id)
        : false
    ) &&
    counter < 6
  ) {
    currentNode = currentNode.parentNode;
    counter++;
  }
  if (counter >= 6) return;
  const columnId = currentNode.parentNode.id;
  const taskId = event.dataTransfer.getData("Text");
  if (!columnId || !taskId) return;
  const status = columnId.split("-");
  if (!validStatus.includes(status[0])) return;
  const taskNode = document.getElementById(`${taskId}`);
  if (taskNode.parentNode.id === columnId) return;
  fetch(`/api/task/${taskId}`, {
    method: "PATCH",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      status: status[0],
    }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("An Error occurred...");
      }
    })
    .then((response) => {
      taskNode.parentNode.removeChild(taskNode);
      render_task_card(response.task);
    })
    .catch((error) => console.log(error));
}

function drop(event) {
  event.preventDefault();
  const columnId = event.target.id;
  const taskId = event.dataTransfer.getData("Text");
  if (!columnId || !taskId) return;
  const status = columnId.split("-");
  if (!validStatus.includes(status[0])) return;
  const taskNode = document.getElementById(`${taskId}`);

  if (taskNode.parentNode.id === columnId) return;
  fetch(`/api/task/${taskId}`, {
    method: "PATCH",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      status: status[0],
    }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("An Error occurred...");
      }
    })
    .then((response) => {
      taskNode.parentNode.removeChild(taskNode);
      render_task_card(response.task);
    })
    .catch((error) => console.log(error));
}

function invite_user({ board_id }) {
  document.querySelector("#invite-error").innerHTML = "";
  const username = document.querySelector("#username-input").value;
  const csrftoken = document.getElementsByName("csrfmiddlewaretoken");

  fetch(`/api/boards/${board_id}/invites`, {
    method: "PATCH",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": csrftoken[0].value,
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username,
    }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("User not found.");
      }
    })
    .then((response) => {
      user_list.push(response.user);
      let invitedContainer = document.querySelector("#invited-container");

      let userNode = document.createElement("span");
      userNode.setAttribute("class", "d-flex flex-row my-1 align-items-center");
      userNode.setAttribute("id", response.user.username);
      userNode.innerHTML = `<strong class='flex-grow-1'>${response.user.username}</strong><button class='btn btn-danger btn-sm' id='remove-${response.user.username}'>Remove</button>`;
      invitedContainer.appendChild(userNode);
      document
        .querySelector(`#remove-${response.user.username}`)
        .addEventListener("click", () =>
          delete_invited_user({ board_id, username: response.user.username })
        );
    })
    .catch(
      (error) =>
        (document.querySelector("#invite-error").innerHTML = error.message)
    );
}
function delete_invited_user({ board_id, username }) {
  document.querySelector("#invite-error").innerHTML = "";
  const csrftoken = document.getElementsByName("csrfmiddlewaretoken");

  fetch(`/api/boards/${board_id}/invites`, {
    method: "DELETE",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": csrftoken[0].value,
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username,
    }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("You can't remove yourself.");
      }
    })
    .then((response) => {
      user_list = user_list.filter((user) => user.id !== response.user.id);
      let invitedUser = document.querySelector(`#${response.user.username}`);
      invitedUser.parentNode.removeChild(invitedUser);
    })
    .catch(
      (error) =>
        (document.querySelector("#invite-error").innerHTML = error.message)
    );
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

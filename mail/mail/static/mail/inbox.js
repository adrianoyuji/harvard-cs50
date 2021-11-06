document.addEventListener("DOMContentLoaded", function () {
  // Use buttons to toggle between views
  document
    .querySelector("#inbox")
    .addEventListener("click", () => load_mailbox("inbox"));
  document
    .querySelector("#sent")
    .addEventListener("click", () => load_mailbox("sent"));
  document
    .querySelector("#archived")
    .addEventListener("click", () => load_mailbox("archive"));
  document.querySelector("#compose").addEventListener("click", compose_email);
  document
    .querySelector("#compose-form")
    .addEventListener("submit", submit_email);

  // By default, load the inbox
  load_mailbox("inbox");
});

function submit_email(e) {
  e.preventDefault();
  const recipients = document.querySelector("#compose-recipients").value;
  const subject = document.querySelector("#compose-subject").value;
  const body = document.querySelector("#compose-body").value;

  fetch("/emails", {
    method: "POST",
    body: JSON.stringify({
      recipients,
      subject,
      body,
    }),
  })
    .then((response) => response.json())
    .then((result) => {
      // Print result
      load_mailbox("inbox");
    });
}

function compose_email() {
  // Show compose view and hide other views
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#email-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "block";

  // Clear out composition fields
  document.querySelector("#compose-recipients").value = "";
  document.querySelector("#compose-subject").value = "";
  document.querySelector("#compose-body").value = "";
}

function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector("#emails-view").style.display = "block";
  document.querySelector("#email-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "none";

  // Show the mailbox name
  document.querySelector("#emails-view").innerHTML = `<h3>${
    mailbox.charAt(0).toUpperCase() + mailbox.slice(1)
  }</h3>
  `;

  fetch(`/emails/${mailbox}`)
    .then((response) => response.json())
    .then((emails) => {
      emails.forEach((email) => {
        let emailDiv = document.createElement("div");

        if (email.read) {
          emailDiv.setAttribute("class", "inbox-item read-email");
        } else {
          emailDiv.setAttribute("class", "inbox-item unread-email");
        }

        emailDiv.setAttribute("id", `email-${email.id}`);

        emailDiv.innerHTML = `
            <span class='inbox-sender'><b>From: </b>${email.sender}</span>
            <span class='inbox-subject'>${email.subject}</span>
            <span class='inbox-timestamp'>${email.timestamp}</span>
          `;
        document.querySelector("#emails-view").appendChild(emailDiv);
        document
          .querySelector(`#email-${email.id}`)
          .addEventListener("click", () => view_email(email.id, mailbox));
      });
    });
}
function view_email(id, mailbox) {
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#email-view").style.display = "block";
  document.querySelector("#compose-view").style.display = "none";

  document.querySelector("#email-view").innerHTML = "";

  fetch(`/emails/${id}`)
    .then((response) => response.json())
    .then((email) => {
      if (!email.read) {
        fetch(`/emails/${id}`, {
          method: "PUT",
          body: JSON.stringify({
            read: true,
          }),
        });
      }

      let emailDiv = document.createElement("div");
      emailDiv.setAttribute("class", `view-email-details`);
      emailDiv.innerHTML = `
            <span><b>From: </b>${email.sender}</span>
            <span><b>To: </b>${email.recipients.map(
              (recipient) => ` ${recipient}`
            )}</span>
            <span><b>Subject: </b>${email.subject}</span>
            <span><b>Timestamp: </b>${email.timestamp}</span>
            <div class="button-container">
              <button class="btn btn-sm btn-outline-primary" id="reply-${id}">Reply</button>
              ${
                mailbox !== "sent"
                  ? `<button
                    class="btn btn-sm btn-outline-primary"
                    id="archive-${id}"
                  >
                    ${email.archived ? "Unarchive" : "Archive"}
                  </button>`
                  : ""
              }
            </div>
            <hr style="height: 1px; width: 100%; color: gray;">
            <p>${email.body}</p>
          `;
      document.querySelector("#email-view").append(emailDiv);
      document
        .querySelector(`#reply-${id}`)
        .addEventListener("click", () => reply_email(email));
      document
        .querySelector(`#archive-${id}`)
        .addEventListener("click", () => archive_email(id, email.archived));
    });
}

function archive_email(id, is_archived) {
  fetch(`/emails/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      archived: !is_archived,
    }),
  }).then((response) => load_mailbox("inbox"));
}

function reply_email(email) {
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#email-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "block";

  document.querySelector("#compose-recipients").value = email.sender;
  document.querySelector("#compose-subject").value = email.subject.startsWith(
    "Re: "
  )
    ? email.subject
    : `Re: ${email.subject}`;
  document.querySelector(
    "#compose-body"
  ).value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`;
}

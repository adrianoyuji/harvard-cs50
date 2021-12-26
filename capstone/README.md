Harvard's CS50 Web Programming with Python and Javascript 2020

---

### **_Final Project: Capstone by Adriano Yuji Sato de Vasconcelos_**

Project Name: **Kanban Board**

## **Introduction**

---

The application I decided to build is a Kanban Board, it is a Project Management Tool that is designed to help people visualize their work, using columns and cards to specify their task.

## **Project distinctiveness and complexities**

---

This project differs from the previous ones due to the fact that it is an Agile Methodology Tool, where users may use this application to help their work progression and organization.

The Kanban board features five columns:

- Backlog;
- To do;
- In Progress;
- Done;
- Closed.

Each column represents the current progression of a Task. A Task contains the Title and a small description of what objective needs to be achieved. The user can change the status of a board by either dragging and dropping the card to the desired column or by editing the status value of the task directly.

This application features the ability to invite other users to collaborate in your boards. Other users can create, read, update and delete Tasks, also, users can assign other users as task assignee and/or task reviewer. Furthermore, this web app features a simple notification system, whenever a user:

- assigns you as reviewer/assignee;
- invites you to join a board;
- changes a task status;

The users that are related to those action will receive a message on their notifications list.

This Project also contains:

- Advanced JavaScript features:
  - _ondrag_, _ondrop_ and _ondragover_ events;
  - Error handling with **throw** function;
  - Usage of JavaScript's window interface;
  - Usage of most popular HTTP methods (GET, POST, PUT, PATCH and DELETE) implementing their respective semantic action.
- Usage of Bootstrap v5.1:
  - Usage of Bootstrap's Layout system;
  - Usage of Bootstrap Components;
  - Usage of Bootstrap classes;
- Mobile friendly:
  - The layout changes according to your device screen size;
  - You can accomplish every functionality on any device;
- Django backend:
  - API like urls;
  - 4 Models;
  - Many-to-Many and Many-to-One relationships;
  - Error handling with _try_ and _except_;
  - Change user password;
- Pages with required authorization access:
  - An user can invite other users to collaborate with their work;
  - If an user tries to access a Board that he is not allowed to, will be blocked and redirected;
- Django Testing:
  - API Unit Testing;

## **Files**

---

The following chart is the file structure of this project, it follows the standard Django folder structure so I decided to ommit some default or unaltered files.

```
.
├─ README.md --> this file.
├─ manage.py --> Django's main cli file.
├─ capstone --> Django's main project folder.
│  ├─ settings.py --> Django project settings.
│  └─ ... --> Other default django files.
│
└─ kanban
   ├─ migrations --> folder with db migrations
   ├─ static
   |   └─ kanban
   |       ├─ board.js --> holds '/board/<str:pk>' API calls and functions.
   |       ├─ boards.js --> holds '/boards' API calls and functions.
   |       ├─ notifications.js --> holds '/notifications' API calls and functions.
   |       ├─ script.js --> holds global functions.
   |       └─ styles.css --> holds global styling.
   ├─ templates
   |   └─ kanban
   |       ├─ board.html --> '/board/<str:pk>' page view.
   |       ├─ boards.html --> '/boards' page view.
   |       ├─ index.html --> '/' page view.
   |       ├─ layout.html --> page header with navigation links.
   |       ├─ login.html --> '/login' page view.
   |       ├─ notifications.html --> '/notifications' page view.
   |       ├─ profile.html --> '/profile' page view.
   |       └─ register.html --> '/register' page view.
   ├─ models.py --> holds the db models and serializers.
   ├─ tests.py --> holds the tests cases for this app.
   ├─ urls.py --> holds the available urls of this app.
   ├─ views.py --> holds all the endpoint responses of this app.
   └─ ... --> other django's unaltered files.
```

## **Models**

---

This project contains four main models:

### **User**: Default Django user model.

### **Board**: The Kanban Board itself.

- **Title:** The board title;
- **Description:** The board description;
- **Owner:** The creator of the board;
- **Allowed Users:** A list of users with permission to access this board;
- **Tasks:** A list of _Tasks_;

### **Task**: A Kanban work item.

- **Title:** The task title;
- **Description:** The task description;
- **Owner:** The creator of the task;
- **Assignee:** The assignee of the task;
- **Reviewer:** The reviewer of the task;
- **Status:** Current Status of the task (backlog, to do, in progress, done or closed)
- **Board:** The Board that this task is related to;

### **Notification**: Sent to User's notification inbox.

- **Message:** The notification message;
- **Recipient:** The creator of the task;
- **Board:** The Board that this notification is related to;

## **Installation and running application**

---

This project follows the standard process to run a Django project. Therefore you must have Django installed.

```
pip install django
```

After cloning this repository with _git_, you should run the following commands:

```
python manage.py migrate

python manage.py runserver
```

After these commands you an access the application at

```
http://127.0.0.1:8000/
```

## **Tests**

---

To run tests, you can simply execute this command:

```
python manage.py test
```

## **Instructions**

---

To access this projects features you must register an account, you can access the `/register` page in order to create an account.

After creating an account your navigation bar will display new links. Clicking on `Boards` will redirect you to the page where you can create new Boards or access/edit previous created boards.

Clicking on `View` on a created Board will redirect you to the Kanban Board. By clicking on `New` of any available column will allow you to create a `Task`.

You can change the status of a Task by dragging and dropping it on the desired column on Desktop, on mobile you have to click on `edit` of the Task and change the status value on the select input and then click `Save`.

## **Conclusion**

---

Since I am a frontend developer, developing the interface of this application without the aid of a robust user interface library like React and other npm packages proved to be somewhat challenging. Writing considerably simple features took much more effort to be accomplished without the amenities of a framework, this proved to be a valuable lesson since I can now understand how most frontend libraries work behind the scenes.

Since I have solid knowledge of Algorithms and Data Structures, Python proved to be a really easy and fun new language to learn, you can accomplish so much with so little. Also, Django and Django Models proved to be extremely easy to work with, it offers a really basic folder architecture and contains a really helpful CLI to aid the developer.

CS50 Web Programming with Python and Javascript proved to be really fun and the knowledge transmitted was really valuable, each project featured new possibilities to expand my knowledge as a developer. It teaches the basics of Web Programming but also teaches how huge it can get, and proves that learning is a constant process.

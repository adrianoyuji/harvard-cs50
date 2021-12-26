from django.test import TestCase, Client
from .models import Board, Notification, Task, User
import json

csrf_client = Client(enforce_csrf_checks=True)


class KanbanAPITestCase(TestCase):
    def setUp(self):
        registeredUser = User.objects.create_user(
            username="registereduser", password="1234", email="registereduser@email.com"
        )
        Board.objects.create(
            title="Fake board",
            description="placeholder text",
            owner=User.objects.get(id=registeredUser.id),
        )

    def test_registration(self):
        c = Client()
        response = c.post(
            "/register",
            {
                "username": "testuser",
                "password": "1234",
                "confirmation": "1234",
                "email": "testuser@email.com",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["user"].username, "testuser")
        self.assertEqual(response.context["user"].email, "testuser@email.com")
        print("Testing Register User -- OK")

    def test_registration_different_passwords(self):
        c = Client()
        response = c.post(
            "/register",
            {
                "username": "testuser",
                "password": "4321",
                "confirmation": "1234",
                "email": "testuser@email.com",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["message"], "Passwords must match.")
        print("Testing differente register password -- OK")

    def test_registration_username_taken(self):
        c = Client()
        response = c.post(
            "/register",
            {
                "username": "registereduser",
                "password": "1234",
                "confirmation": "1234",
                "email": "registereduser@email.com",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["message"], "Username already taken.")
        print("Testing username taken -- OK")

    def test_login(self):
        c = Client()
        response = c.post(
            "/login",
            {
                "username": "registereduser",
                "password": "1234",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["user"].username, "registereduser")
        print("Testing Login -- OK")

    def test_login_failed(self):
        c = Client()
        response = c.post(
            "/login",
            {
                "username": "testuser",
                "password": "1234",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["message"], "Invalid username and/or password."
        )
        print("Testing Login invalid username/pwd -- OK")

    def test_get_board(self):
        fakeUser = User.objects.create_user(
            username="testuser", password="1234", email="testuser@email.com"
        )
        testBoard = Board.objects.create(
            title="Test Board",
            description="this is a test board",
            owner=User.objects.get(id=fakeUser.id),
        )
        c = Client()
        c.login(username="testuser", password="1234")
        response = c.get("/api/boards")
        data = response.json()
        self.assertEqual(list(data["boards"])[0]["id"], testBoard.id)
        self.assertEqual(list(data["boards"])[0]["title"], testBoard.title)
        self.assertEqual(list(data["boards"])[0]["description"], testBoard.description)
        self.assertEqual(list(data["boards"])[0]["owner"]["id"], fakeUser.id)
        print("Testing Get Board -- OK")

    def test_creat_board(self):
        c = Client()
        c.login(username="registereduser", password="1234")
        response = c.post(
            "/api/boards",
            json.dumps(
                {"title": "Testing board", "description": "I am testing this board"}
            ),
            "json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = response.json()
        self.assertEqual(data["message"], "Board created successfully.")
        self.assertTrue(Board.objects.get(pk=data["board"]["id"]))
        print("Testing Create Board -- OK")

    def test_board_doesnot_exist(self):
        c = Client()
        c.login(username="registereduser", password="1234")
        response = c.get("/api/boards/200")
        data = response.json()
        self.assertEqual(data["message"], "Board not found.")
        print("Testing Board does not exist -- OK")

    def test_get_board(self):
        c = Client()
        c.login(username="registereduser", password="1234")
        response = c.get("/api/boards/1")
        data = response.json()
        self.assertEqual(data["board"]["id"], 1)
        self.assertEqual(data["board"]["title"], "Fake board")
        self.assertEqual(data["board"]["description"], "placeholder text")
        print("Testing Get board -- OK")

    def test_update_board(self):
        c = Client()
        c.login(username="registereduser", password="1234")
        response = c.put(
            "/api/boards/1",
            json.dumps(
                {"title": "Updated board", "description": "I am updating this board"}
            ),
            "json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = response.json()
        self.assertEqual(data["message"], "Board updated.")
        updatedBoard = Board.objects.get(id=1)
        self.assertEqual(updatedBoard.title, "Updated board")
        self.assertEqual(updatedBoard.description, "I am updating this board")
        print("Testing Update board -- OK")

    def test_delete_board(self):
        c = Client()
        c.login(username="registereduser", password="1234")
        response = c.delete(
            "/api/boards/1",
        )
        data = response.json()
        self.assertEqual(data["message"], "Board successfuly deleted.")
        self.assertFalse(Board.objects.filter(id=1).exists())
        print("Testing Delete board -- OK")

    def test_invite_user(self):
        randomUser = User.objects.create_user(
            username="randomuser", password="1234", email="randomuser@email.com"
        )
        c = Client()
        c.login(username="registereduser", password="1234")
        response = c.patch(
            "/api/boards/1/invites",
            json.dumps({"username": randomUser.username}),
            "json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = response.json()
        self.assertEqual(data["user"]["id"], randomUser.id)
        self.assertTrue(Board.objects.get(id=1).allowed_users.get(id=randomUser.id))
        print("Testing Invite an User -- OK")

        response = c.patch(
            "/api/boards/1/invites",
            json.dumps({"username": randomUser.username}),
            "json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = response.json()
        self.assertEqual(data["message"], "User already invited.")
        print("Testing Already Invited User -- OK")

        response = c.delete(
            "/api/boards/1/invites",
            json.dumps({"username": randomUser.username}),
            "json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = response.json()
        self.assertFalse(
            Board.objects.get(id=1).allowed_users.filter(id=randomUser.id).exists()
        )
        print("Testing Remove Invited User -- OK")

    def test_board_task(self):
        c = Client()
        c.login(username="registereduser", password="1234")
        response = c.post(
            "/api/board/1/task",
            json.dumps(
                {
                    "title": "Test task",
                    "description": "test description",
                    "status": "todo",
                    "assignee_id": "0",
                    "reviewer_id": "0",
                }
            ),
            "json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = response.json()
        self.assertEqual(data["message"], "Board created successfully.")
        self.assertTrue(Task.objects.get(id=data["task"]["id"]))
        print("Testing Create Board Task -- OK")

        response = c.get(
            f"/api/task/{data['task']['id']}",
        )
        data = response.json()
        self.assertEqual(data["message"], "Task found.")
        self.assertTrue(Task.objects.get(id=data["task"]["id"]))
        print("Testing Getting Created Task -- OK")

        response = c.patch(
            f"/api/task/{data['task']['id']}",
            json.dumps({"status": "done"}),
            "json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = response.json()
        self.assertEqual(data["message"], "Task found.")
        self.assertEqual(Task.objects.get(id=data["task"]["id"]).status, "done")
        print("Testing Updating Task Status -- OK")

        response = c.put(
            f"/api/task/{data['task']['id']}",
            json.dumps(
                {
                    "title": "Updated Test task",
                    "description": "updated test description",
                    "status": "done",
                    "assignee_id": "1",
                    "reviewer_id": "1",
                }
            ),
            "json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        updatedData = response.json()
        self.assertEqual(updatedData["message"], "Task updated.")
        self.assertEqual(
            Task.objects.get(id=data["task"]["id"]).title, "Updated Test task"
        )
        self.assertEqual(
            Task.objects.get(id=data["task"]["id"]).description,
            "updated test description",
        )
        print("Testing Update Task -- OK")

        response = c.delete(
            f"/api/task/{data['task']['id']}",
        )
        deleteData = response.json()
        self.assertEqual(deleteData["message"], "Task delete.")
        self.assertFalse(Task.objects.filter(id=data["task"]["id"]).exists())
        print("Testing Delete Task -- OK")

    def test_notifications(self):
        user = User.objects.get(id=1)
        user.notifications.add(
            Notification.objects.create(
                board=Board.objects.get(id=1),
                message=f"Notification Test",
                recipient=user,
            )
        )

        c = Client()
        c.login(username="registereduser", password="1234")
        response = c.get(
            "/api/notifications?page=1",
        )
        data = response.json()
        self.assertEqual(data["notifications"][0]["message"], "Notification Test")
        print("Testing Get Notifications -- OK")

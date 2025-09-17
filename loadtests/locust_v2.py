import random
from uuid import uuid4

from locust import FastHttpUser, task, constant_pacing
from locust.exception import StopUser


class V2ApiUser(FastHttpUser):
    """模拟登录、发帖、投票的 V2 API 高并发场景"""

    wait_time = constant_pacing(0.1)

    def on_start(self):
        self.auth_headers = {}
        self.known_post_ids = set()
        self._register_and_login()
        self._create_post(seed=True)

    def _register_and_login(self):
        """注册唯一用户并获取 token"""
        self.email = f"locust_{uuid4().hex}@example.com"
        self.password = "Locust!234"

        with self.client.post(
            "/v2/users/",
            json={"email": self.email, "password": self.password},
            name="POST /v2/users",
            catch_response=True,
        ) as response:
            if response.status_code != 201:
                response.failure(f"注册失败: {response.status_code} {response.text}")
                raise StopUser()
            response.success()

        with self.client.post(
            "/v2/auth/login",
            data={"username": self.email, "password": self.password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            name="POST /v2/auth/login",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"登录失败: {response.status_code} {response.text}")
                raise StopUser()

            token = response.json().get("access_token")
            if not token:
                response.failure("登录成功但未返回 token")
                raise StopUser()

            self.auth_headers = {"Authorization": f"Bearer {token}"}
            response.success()

    def _create_post(self, seed: bool = False):
        payload = {
            "title": f"Locust post {uuid4().hex}",
            "content": "压力测试内容",
            "published": True,
        }
        with self.client.post(
            "/v2/posts/",
            headers=self.auth_headers,
            json=payload,
            name="POST /v2/posts",
            catch_response=True,
        ) as response:
            if response.status_code == 201:
                post_id = response.json()["id"]
                self.known_post_ids.add(post_id)
                response.success()
            else:
                response.failure(f"发帖失败: {response.status_code} {response.text}")
                if seed:
                    raise StopUser()

    @task(3)
    def list_posts(self):
        with self.client.get(
            "/v2/posts/",
            headers=self.auth_headers,
            name="GET /v2/posts",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                for item in response.json():
                    post = item.get("post")
                    if post and "id" in post:
                        self.known_post_ids.add(post["id"])
                response.success()
            else:
                response.failure(f"拉取帖子失败: {response.status_code} {response.text}")

    @task(2)
    def create_post_task(self):
        self._create_post()

    @task(2)
    def vote_task(self):
        if not self.known_post_ids:
            return

        post_id = random.choice(tuple(self.known_post_ids))
        direction = random.choice([0, 1])

        with self.client.post(
            "/v2/vote/",
            headers=self.auth_headers,
            json={"post_id": post_id, "dir": direction},
            name="POST /v2/vote",
            catch_response=True,
        ) as response:
            if response.status_code == 201:
                response.success()
            elif direction == 0 and response.status_code == 404:
                response.success()
            elif direction == 1 and response.status_code == 409:
                response.success()
            else:
                response.failure(
                    f"投票失败: dir={direction} status={response.status_code} body={response.text}"
                )

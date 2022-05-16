from locust import HttpUser, SequentialTaskSet, task


class MyTasks(SequentialTaskSet):
    # when locust file start executing on_start() will be called first
    def on_start(self):
        self.client.get("/")

    @task
    def login(self):
        self.client.post("/showSummary",
                         {
                             "email": "john@simplylift.co"
                         })

    @task
    def booking_page(self):
        self.client.get("/book/New%20Competition/Simply%20Lift")

    @task
    def purchase_places(self):
        self.client.post("/purchasePlaces",
                         {
                             "competition": "New Competition",
                             "club": "Simply Lift",
                             "places": "1"
                         })

    @task
    def display_clubs(self):
        self.client.post("/clubs",
                         {
                             "email": "john@simplylift.co"
                         })

    @task
    def logout(self):
        self.client.get("/logout")


class MyWebsiteUser(HttpUser):
    tasks = [MyTasks]
    min_wait = 100  # miliseconds
    max_wait = 5000  # miliseconds
    # same as wait_time = between(0.100, 5)
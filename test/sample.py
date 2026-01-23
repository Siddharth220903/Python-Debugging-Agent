class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def can_vote(self):
        if self.age >= 18:
            return True
        else:
            return False

def process_users(users):
    results = []
    for user in users:
        results.append({"name": user.name, "can_vote": user.can_vote()})

    return results

users = [
    User("Alice", 30),
    User("Bob", 15),
]

print(process_users(users))
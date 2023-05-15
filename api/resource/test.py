class Student:
    def __init__(self, name, age, gender, student_id):
        self.name = name
        self.age = age
        self.gender = gender
        self.student_id = student_id

s = {
    "name":"wu",
    "age":18,
    "gender": "男",
    "student_id": 124,
    "grade": 123
}
st = Student(**s)
print(st)
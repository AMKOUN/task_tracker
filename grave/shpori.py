

# CREATE - добавление данных
def add_student(name, age):
    # TODO: Создать нового студента и добавить в сессию
    new_student = Student(name=name, age=age)
    session.add(new_student)
    session.commit()
    print(f"Студент {name} добавлен")


# READ - получение данных
def get_all_students():
    # TODO: Вернуть всех студентов
    return session.query(Student).all()


def find_student_by_name(name):
    # TODO: Найти студента по имени
    return session.query(Student).filter(Student.name == name).first()


# UPDATE - обновление данных
def update_student_age(student_id, new_age):
    student = session.query(Student).get(student_id)
    if student:
        # TODO: Обновить возраст студента
        student.age = new_age
        session.commit()
        return True
    return False


# DELETE - удаление данных
def delete_student(student_id):
    student = session.query(Student).get(student_id)
    if student:
        # TODO: Удалить студента
        session.delete(student)
        session.commit()
        return True
    return False


def get_students_older_than(age):
    # TODO: Вернуть студентов старше указанного возраста
    return session.query(Student).filter(Student.age > age).all()


def get_courses_like(keyword):
    # TODO: Вернуть курсы, в названии которых есть ключевое слово
    return session.query(Course).filter(Course.title.like(f"%{keyword}%")).all()


def count_students():
    # TODO: Вернуть количество студентов
    return session.query(Student).count()


class Student(Base):
    __tablename__ = 'students'

    # TODO: Добавить поля: id (первичный ключ), name (строка), age (целое число)
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer)

    enrollments = relationship('Enrollment', back_populates='student')

    def __repr__(self):
        return f"<Student(id={self.id}, name='{self.name}', age={self.age})>"


class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True)
    # TODO: Добавить поле title (строка, обязательно для заполнения)
    title = Column(String, nullable=False)

    # связь с Enrollment
    enrollments = relationship('Enrollment', back_populates='course')

    def repr(self):
        return f"<Course(id={self.id}, title='{self.title}')>"


class Enrollment(Base):
    __tablename__ = 'enrollments'

    id = Column(Integer, primary_key=True)
    # TODO: Добавить внешние ключи student_id и course_id
    student_id = Column(Integer, ForeignKey('students.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))

    # TODO: Добавить отношения к Student и Course
    student = relationship('Student', back_populates='enrollments')
    course = relationship('Course', back_populates='enrollments')



def main():
    # Создание таблиц
    Base.metadata.create_all(engine)

    # TODO: Добавить тестовых студентов
    add_student("Петя", 23)
    add_student("Мария", 20)

    # TODO: Добавить тестовые курсы
    math = Course(title="Математика")
    physics = Course(title="Физика")
    session.add_all([math, physics])
    session.commit()

    # TODO: Записать студентов на курсы
    ivan = find_student_by_name("Иван")
    masha = find_student_by_name("Мария")

    session.add_all([
        Enrollment(student=ivan, course=math),
        Enrollment(student=masha, course=physics)
    ])
    session.commit()

    # TODO: Показать всех студентов
    students = get_all_students()
    print("Все студенты:", students)

    # TODO: Найти студента по имени
    student = find_student_by_name("Иван")
    print("Найден студент:", student)

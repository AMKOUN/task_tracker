import datetime
from sqlalchemy import create_engine, Column, Integer, Boolean, String, DateTime, ForeignKey, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# TODO: Создать движок для SQLite базы данных 'school.db'
engine = create_engine('sqlite:///school.db', echo=True)
with engine.connect() as connection:
    result = connection.execute(text("SELECT sqlite_version();"))
    print(result.fetchone())

Base = declarative_base()

# TODO: Создать фабрику сессий и экземпляр сессии
Session = sessionmaker(bind=engine)
session = Session()

# TODO: Создать все таблицы в базе данных
Base.metadata.create_all(engine)


class Task(Base):
    __tablename__ = 'tasks'

    # TODO: Добавить поля: id (первичный ключ), name (строка), age (целое число)
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, nullable=False)
    done = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    users = relationship('User', back_populates='user')

    def __repr__(self):
        return f"<Task(id={self.id}, status='{self.status}', description='{self.description}', title='{self.title}', description={self.description})>"


class User(Base):
    __tablename__ = 'users'

    # TODO: Добавить поля: id (первичный ключ), name (строка), age (целое число)
    user_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String, nullable=False)
    tasks = relationship('Task', back_populates='task')

    def __repr__(self):
        return f"<Task(id={self.id}, status='{self.status}', description='{self.description}', title='{self.title}', description={self.description})>"


def main():
    # Создание таблиц
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()
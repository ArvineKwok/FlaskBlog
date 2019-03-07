from faker import Faker

from blog.models import Post, Category, Comment, Admin
from blog.extensions import db
import random


fake = Faker()

def fake_admin():
    admin = Admin(
        username='admin',
        blog_title='Home',
        blog_sub_title='I can you can too',
        name='Arvine',
        about='I\'am on my way.'
    )
    admin.password='helloflask'
    db.session.add(admin)
    db.session.commit()

def fake_posts(count=50):
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            category=Category.query.get(random.randint(1, Category.query.count())),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(post)
    db.session.commit()


def fake_comments(count=500):
    for i in range(count):
        comment = Comment(
            body=fake.sentence(),
            author=fake.name(),
            email=fake.email(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    salt = int(count * 0.1)
    for i in range(salt):
        comment = Comment(
            body=fake.sentence(),
            author=fake.name(),
            email=fake.email(),
            timestamp=fake.date_time_this_year(),
            reviewed=False,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )

        db.session.add(comment)

        comment = Comment(
            body=fake.sentence(),
            author='Arinve',
            email='arvine@example.com',
            timestamp=fake.date_time_this_year(),
            from_admin=True,
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()

    for i in range(salt):
        comment = Comment(
            body=fake.sentence(),
            author=fake.name(),
            email=fake.email(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            replied=Comment.query.get(random.randint(1, Comment.query.count())),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()


def fake_categories(count=10):
    default = Category(name='Default')
    db.session.add(default)
    for i in range(count):
        category = Category(
            name=fake.word()
        )
        try:
            db.session.add(category)
        except:
            db.session.rollback()
    db.session.commit()

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required
from blog.forms import PostForm, CategoryForm
from blog.models import Post, Category
from blog.extensions import db


admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
def login_protect():
    pass

@admin_bp.route('/post/new', methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category_id = form.category.data
        post = Post(title=title, body=body, category_id=category_id)
        db.session.add(post)
        db.session.commit()
        flash('Post created.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    return render_template('admin/new_post.html', form=form)

@admin_bp.route('/category/new', methods=['GET', 'POST'])
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('Category created.', 'success')
        return redirect(url_for('blog.index'))
    return render_template('admin/new_category.html', form=form)
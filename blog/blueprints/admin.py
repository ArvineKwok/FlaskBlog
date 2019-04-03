from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request
from flask_login import login_required
from blog.forms import PostForm, CategoryForm, SettingForm
from blog.models import Post, Category, Comment, Admin
from blog.extensions import db
from blog.utils import redirect_back

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


@admin_bp.route('/category/manage')
def manage_category():
    return render_template('admin/manage_category.html')

@admin_bp.route('/category/edit/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm()
    if category.id == 1:
        flash('You can not edit the default category.', 'warning')
        return redirect(url_for('blog.index'))
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category updated.', 'success')
        return redirect(url_for('.manage_category'))
    form.name.data = category.name
    return render_template('admin/edit_category.html', form=form)

@admin_bp.route('/category/delete/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('You can not delete the default category.', 'warning')
        return redirect(url_for('blog.index'))
    category.delete()
    flash('Category deleted.', 'success')
    return redirect(url_for('.manage_category'))

@admin_bp.route('/post/manage')
def manage_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOG_MANAGE_POST_PER_PAGE'])
    posts = pagination.items
    return render_template('admin/manage_post.html', posts=posts, pagination=pagination)

@admin_bp.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)

    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category = Category.query.get(form.category.data)
        db.session.add(post)
        db.session.commit()
        flash('Post updated.', 'success')
        return redirect(url_for('.manage_post'))
    form.title.data = post.title
    form.category.data = post.category.id
    form.body.data = post.body
    return render_template('admin/edit_post.html', form=form)

@admin_bp.route('/post/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect_back()

@admin_bp.route('/comment/manage')
def manage_comment():
    filter_rule = request.args.get('filter', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_COMMENT_PER_PAGE']
    if filter_rule == 'unread':
        filtered_comments = Comment.query.filter_by(reviewed=False)
    elif filter_rule == 'admin':
        filtered_comments = Comment.query.filter_by(from_admin=True)
    else:
        filtered_comments = Comment.query

    pagination = filtered_comments.order_by(Comment.timestamp.desc()).paginate(page, per_page=per_page)
    comments = pagination.items
    return render_template('admin/manage_comment.html', pagination=pagination, comments=comments)

@admin_bp.route('/comment/delete/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    return redirect_back()

@admin_bp.route('/comment/approve/<int:comment_id>', methods=['POST'])
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.reviewed = True
    db.session.commit()
    flash('Comment approved.', 'success')
    return redirect_back()


@admin_bp.route('/setting', methods=['GET', 'POST'])
@login_required
def setting():
    admin = Admin.query.first()
    form = SettingForm()
    if form.validate_on_submit():
        admin.name = form.name.data
        admin.blog_title = form.blog_title.data
        admin.blog_sub_title = form.blog_sub_title.data
        admin.about = form.about.data
        db.session.add(admin)
        db.session.commit()
        return redirect(url_for('blog.index'))
    form.name.data = admin.name
    form.blog_title.data = admin.blog_title
    form.blog_sub_title.data = admin.blog_sub_title
    form.about.data = admin.about
    return render_template('admin/setting.html', form=form)


@admin_bp.route('/post/<int:post_id>/set-comment', methods=['POST'])
@login_required
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if post.can_comment:
        post.can_comment = False
        flash('Comment disabled.', 'success')
    else:
        post.can_comment = True
        flash('Comment enabled.', 'success')
    db.session.commit()
    return redirect_back()
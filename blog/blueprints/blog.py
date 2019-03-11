from flask import render_template, Blueprint, current_app, request, flash, redirect, url_for
from blog.models import Post, Comment, Category
from blog.forms import CommentForm, AdminCommentForm
from blog.extensions import db
from flask_login import current_user
blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/index.html', posts=posts, pagination=pagination)


@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_COMMENT_PER_PAGE']

    pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.desc()).paginate(page, per_page=per_page)
    comments = pagination.items
    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config['BLUELOG_EMAIL']
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False

    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        body = form.body.data
        comment = Comment(
            author=author, email=email, body=body,
            from_admin=from_admin, post=post, reviewed=reviewed
        )
        replied_id = request.args.get('reply')
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
        db.session.add(comment)
        db.session.commit()
        flash('Thanks, your comment will be published after reviewed.', 'info')
        return redirect(url_for('.show_post', post_id=post_id))
    return render_template('blog/post.html', post=post, pagination=pagination, comments=comments, form=form)

@blog_bp.route('/about')
def about():
    return render_template('blog/about.html')

@blog_bp.route('/categories')
def categories():
    return render_template('blog/categories.html')

@blog_bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment.post.can_comment:
        flash('Comment is disabled.', 'warning')
        return redirect(url_for('.show_post', post_id=comment.post.id))
    return redirect(
        url_for('.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + '#comment-form')

@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    posts = Post.query.with_parent(category).order_by(Post.timestamp.desc())
    return render_template('blog/show_categroy.html', category=category, posts=posts)
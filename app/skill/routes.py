from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import db
from app.models import SkillPost, ConnectionRequest, Rating, User

skill = Blueprint('skill', __name__, url_prefix='/skills')


@skill.route('/')
def index():
    post_type = request.args.get('type', 'all').lower()
    if post_type not in ('all', 'offer', 'request'):
        post_type = 'all'
    query = SkillPost.query.join(User)
    if post_type in ('offer', 'request'):
        query = query.filter(SkillPost.post_type == post_type)
    keyword = request.args.get('q', '').strip()
    if keyword:
        like = f'%{keyword}%'
        query = query.filter(or_(SkillPost.skill_name.ilike(like),
                                 SkillPost.description.ilike(like),
                                 User.name.ilike(like)))
    posts = query.order_by(SkillPost.created_at.desc()).all()
    return render_template('skills.html', posts=posts, post_type=post_type, keyword=keyword)


@skill.route('/new/<post_type>', methods=['GET', 'POST'])
@login_required
def new_post(post_type):
    if post_type not in ('offer', 'request'):
        abort(404)
    if request.method == 'POST':
        skill_name = request.form.get('skill_name', '').strip()
        description = request.form.get('description', '').strip()
        if not skill_name:
            flash('Please enter a skill name.', 'danger')
            return render_template('skill_form.html', post=None, post_type=post_type)
        if len(skill_name) > 100:
            flash('Skill name must be 100 characters or fewer.', 'danger')
            return render_template('skill_form.html', post=None, post_type=post_type)
        post = SkillPost(user_id=current_user.id, skill_name=skill_name,
                         description=description, post_type=post_type)
        db.session.add(post)
        db.session.commit()
        flash('Your skill post has been published!', 'success')
        return redirect(url_for('skill.index', type=post_type))
    return render_template('skill_form.html', post=None, post_type=post_type)


@skill.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = db.get_or_404(SkillPost, post_id)
    if post.user_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        skill_name = request.form.get('skill_name', '').strip()
        description = request.form.get('description', '').strip()
        if not skill_name:
            flash('Please enter a skill name.', 'danger')
        elif len(skill_name) > 100:
            flash('Skill name must be 100 characters or fewer.', 'danger')
        else:
            post.skill_name = skill_name
            post.description = description
            db.session.commit()
            flash('Your post has been updated.', 'success')
            return redirect(url_for('skill.index', type=post.post_type))
    return render_template('skill_form.html', post=post, post_type=post.post_type)


@skill.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = db.get_or_404(SkillPost, post_id)
    if post.user_id != current_user.id:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your skill post has been deleted.', 'success')
    return redirect(url_for('skill.index'))


@skill.route('/<int:post_id>/connect', methods=['POST'])
@login_required
def connect(post_id):
    post = db.get_or_404(SkillPost, post_id)
    if post.user_id == current_user.id:
        flash("You can't send a connection request to your own post.", 'warning')
        return redirect(url_for('skill.index'))
    existing = ConnectionRequest.query.filter(
        ConnectionRequest.sender_id == current_user.id,
        ConnectionRequest.receiver_id == post.user_id
    ).first()
    if existing:
        flash('You already have a connection request or connection with this student.', 'info')
    else:
        db.session.add(ConnectionRequest(sender_id=current_user.id, receiver_id=post.user_id))
        db.session.commit()
        flash('Connection request sent!', 'success')
    return redirect(url_for('skill.index'))


@skill.route('/connections')
@login_required
def connections():
    incoming = ConnectionRequest.query.filter_by(receiver_id=current_user.id).order_by(
        ConnectionRequest.created_at.desc()).all()
    outgoing = ConnectionRequest.query.filter_by(sender_id=current_user.id).order_by(
        ConnectionRequest.created_at.desc()).all()
    return render_template('skill_connections.html', incoming=incoming, outgoing=outgoing)


@skill.route('/connections/<int:request_id>/<action>', methods=['POST'])
@login_required
def respond_connection(request_id, action):
    connection = db.get_or_404(ConnectionRequest, request_id)
    if connection.receiver_id != current_user.id:
        abort(403)
    if action not in ('accept', 'reject'):
        abort(404)
    connection.status = 'accepted' if action == 'accept' else 'rejected'
    db.session.commit()
    flash('Connection ' + ('accepted.' if action == 'accept' else 'declined.'), 'success')
    return redirect(url_for('skill.connections'))


@skill.route('/users/<int:user_id>/rate', methods=['POST'])
@login_required
def rate_user(user_id):
    if user_id == current_user.id:
        flash("You can't rate yourself.", 'warning')
        return redirect(url_for('skill.connections'))
    connected = ConnectionRequest.query.filter(
        or_(
            (ConnectionRequest.sender_id == current_user.id) & (ConnectionRequest.receiver_id == user_id),
            (ConnectionRequest.sender_id == user_id) & (ConnectionRequest.receiver_id == current_user.id)
        ),
        ConnectionRequest.status == 'accepted'
    ).first()
    if not connected:
        abort(403)
    try:
        value = int(request.form.get('rating', ''))
    except ValueError:
        value = 0
    review = request.form.get('review', '').strip()
    if value not in range(1, 6):
        flash('Choose a rating from 1 to 5.', 'danger')
        return redirect(url_for('skill.connections'))
    existing = Rating.query.filter_by(rater_id=current_user.id, rated_user_id=user_id).first()
    if existing:
        existing.rating = value
        existing.review = review
    else:
        db.session.add(Rating(rater_id=current_user.id, rated_user_id=user_id,
                              rating=value, review=review))
    db.session.commit()
    flash('Your rating has been saved.', 'success')
    return redirect(url_for('skill.connections'))

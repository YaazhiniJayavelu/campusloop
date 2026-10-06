import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from PIL import Image
import imagehash
from app import db
from app.models import Item

lostfound = Blueprint('lostfound', __name__)

CATEGORIES = ['Electronics', 'Books & Stationery', 'ID & Cards', 'Keys',
              'Bags', 'Clothing & Accessories', 'Other']
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def save_photo(file):
    """Save the upload and return (filename, hash). Returns (None, None) if invalid."""
    if '.' not in file.filename:
        return None, None
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXT:
        return None, None

    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(path)

    try:
        with Image.open(path) as img:
            img_hash = str(imagehash.phash(img))
    except Exception:
        os.remove(path)
        return None, None
    return filename, img_hash


@lostfound.route('/items')
def items():
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    status = request.args.get('status', '')

    query = Item.query
    if q:
        like = f'%{q}%'
        query = query.filter(db.or_(
            Item.title.ilike(like),
            Item.description.ilike(like),
            Item.location.ilike(like)
        ))
    if category in CATEGORIES:
        query = query.filter_by(category=category)
    if status in ('lost', 'found'):
        query = query.filter_by(status=status)

    all_items = query.order_by(Item.created_at.desc()).all()
    return render_template('items.html', items=all_items, categories=CATEGORIES,
                           q=q, category=category, status=status)

@lostfound.route('/items/new', methods=['GET', 'POST'])
@login_required
def new_item():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '')
        location = request.form.get('location', '').strip()
        status = request.form.get('status', '')

        if not title or not location or category not in CATEGORIES or status not in ('lost', 'found'):
            flash('Please fill in all required fields.', 'danger')
            return render_template('item_form.html', categories=CATEGORIES)

        image_filename, image_hash = None, None
        photo = request.files.get('photo')
        if photo and photo.filename:
            image_filename, image_hash = save_photo(photo)
            if not image_filename:
                flash('Photo must be a valid PNG, JPG, GIF or WEBP image.', 'danger')
                return render_template('item_form.html', categories=CATEGORIES)

        item = Item(title=title, description=description, category=category,
                    location=location, status=status,
                    image_filename=image_filename, image_hash=image_hash,
                    user_id=current_user.id)
        db.session.add(item)
        db.session.commit()
        flash('Item posted.', 'success')
        return redirect(url_for('lostfound.item_detail', item_id=item.id))

    return render_template('item_form.html', categories=CATEGORIES)


@lostfound.route('/items/<int:item_id>')
def item_detail(item_id):
    item = db.get_or_404(Item, item_id)
    return render_template('item_detail.html', item=item)
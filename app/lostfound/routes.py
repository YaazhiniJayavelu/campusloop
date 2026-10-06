import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from PIL import Image
import imagehash
from app import db
from app.models import Item, Claim

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
    my_claim = None
    if current_user.is_authenticated:
        my_claim = (Claim.query
                    .filter_by(item_id=item.id, claimant_id=current_user.id)
                    .order_by(Claim.created_at.desc()).first())
    return render_template('item_detail.html', item=item, my_claim=my_claim)


@lostfound.route('/items/<int:item_id>/claim', methods=['POST'])
@login_required
def send_claim(item_id):
    item = db.get_or_404(Item, item_id)
    if item.user_id == current_user.id:
        flash('You cannot claim your own post.', 'danger')
    elif item.is_resolved:
        flash('This item is already resolved.', 'danger')
    elif Claim.query.filter_by(item_id=item.id, claimant_id=current_user.id,
                               status='pending').first():
        flash('You already sent a claim for this item.', 'warning')
    else:
        claim = Claim(item_id=item.id, claimant_id=current_user.id,
                      message=request.form.get('message', '').strip())
        db.session.add(claim)
        db.session.commit()
        flash('Claim sent. The poster will review it.', 'success')
    return redirect(url_for('lostfound.item_detail', item_id=item.id))

@lostfound.route('/claims/<int:claim_id>/<action>', methods=['POST'])
@login_required
def handle_claim(claim_id, action):
    claim = db.get_or_404(Claim, claim_id)
    item = claim.item

    if item.user_id != current_user.id:
        flash('Only the poster can do that.', 'danger')
    elif claim.status != 'pending' or item.is_resolved:
        flash('This claim was already handled.', 'warning')
    elif action == 'approve':
        claim.status = 'approved'
        item.is_resolved = True
        for other in item.claims:
            if other.id != claim.id and other.status == 'pending':
                other.status = 'rejected'
        db.session.commit()
        flash('Claim approved. Item marked as resolved.', 'success')
    elif action == 'reject':
        claim.status = 'rejected'
        db.session.commit()
        flash('Claim rejected.', 'info')
    else:
        flash('Invalid action.', 'danger')

    return redirect(url_for('lostfound.item_detail', item_id=item.id))
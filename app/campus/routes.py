import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort, send_from_directory
from flask_login import login_required, current_user
from app import db
from app.models import (StudyResource, CampusEvent, EventRegistration, CampusClub,
                        ClubMembership, MarketplaceListing, CampusPoll, PollVote,
                        CampusFeedback)

campus = Blueprint('campus', __name__, url_prefix='/campus')
STUDY_EXT = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt'}
IMAGE_EXT = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def upload_file(field, allowed, prefix):
    f = request.files.get(field)
    if not f or not f.filename:
        return None, None
    original = secure_filename(f.filename)
    ext = original.rsplit('.', 1)[-1].lower() if '.' in original else ''
    if ext not in allowed:
        return False, None
    name = f'{prefix}_{os.urandom(12).hex()}.{ext}'
    folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(folder, exist_ok=True)
    f.save(os.path.join(folder, name))
    return name, original

@campus.route('/')
@login_required
def dashboard():
    return render_template('campus/dashboard.html',
        resource_count=StudyResource.query.count(),
        event_count=CampusEvent.query.count(),
        listing_count=MarketplaceListing.query.filter_by(status='available').count(),
        poll_count=CampusPoll.query.filter_by(is_open=True).count())

@campus.route('/study')
def study():
    q = request.args.get('q','').strip()
    query = StudyResource.query
    if q:
        like = f'%{q}%'
        query = query.filter(db.or_(StudyResource.title.ilike(like),
                                    StudyResource.subject.ilike(like),
                                    StudyResource.description.ilike(like)))
    resources = query.order_by(StudyResource.created_at.desc()).all()
    return render_template('campus/study.html', resources=resources, q=q)

@campus.route('/study/new', methods=['GET','POST'])
@login_required
def study_new():
    if request.method == 'POST':
        title=request.form.get('title','').strip()
        subject=request.form.get('subject','').strip()
        description=request.form.get('description','').strip()
        if not title or len(title)>140 or not subject or len(subject)>100:
            flash('Enter a title (max 140 characters) and subject (max 100).','danger')
        else:
            filename, original=upload_file('file', STUDY_EXT, 'study')
            if filename is False:
                flash('Study files must be PDF, DOC/DOCX, PPT/PPTX or TXT.','danger')
            elif not filename:
                flash('Please choose a study file to upload.','danger')
            else:
                obj=StudyResource(title=title,subject=subject,description=description,
                                  filename=filename,original_filename=original,user_id=current_user.id)
                db.session.add(obj); db.session.commit()
                flash('Study resource shared!','success')
                return redirect(url_for('campus.study'))
    return render_template('campus/study_form.html')

@campus.route('/study/<int:resource_id>/download')
def study_download(resource_id):
    obj=db.get_or_404(StudyResource,resource_id)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'],obj.filename,
                               as_attachment=True,download_name=obj.original_filename or obj.filename)

@campus.route('/study/<int:resource_id>/delete',methods=['POST'])
@login_required
def study_delete(resource_id):
    obj=db.get_or_404(StudyResource,resource_id)
    if obj.user_id != current_user.id: abort(403)
    path=os.path.join(current_app.config['UPLOAD_FOLDER'],obj.filename)
    if os.path.exists(path): os.remove(path)
    db.session.delete(obj); db.session.commit()
    flash('Resource deleted.','success')
    return redirect(url_for('campus.study'))

@campus.route('/events')
def events():
    return render_template('campus/events.html',
        events=CampusEvent.query.order_by(CampusEvent.starts_at.asc()).all(),
        clubs=CampusClub.query.order_by(CampusClub.name.asc()).all())

@campus.route('/events/new',methods=['GET','POST'])
@login_required
def event_new():
    if request.method=='POST':
        title=request.form.get('title','').strip()
        venue=request.form.get('venue','').strip()
        club=request.form.get('club_name','').strip()
        description=request.form.get('description','').strip()
        try: starts=datetime.fromisoformat(request.form.get('starts_at',''))
        except (ValueError,TypeError): starts=None
        if not title or len(title)>140 or not venue or not starts:
            flash('Enter a title, venue and valid date/time.','danger')
        else:
            db.session.add(CampusEvent(title=title,venue=venue,club_name=club,
                description=description,starts_at=starts,created_by=current_user.id))
            db.session.commit(); flash('Event created!','success')
            return redirect(url_for('campus.events'))
    return render_template('campus/event_form.html')

@campus.route('/events/<int:event_id>/register',methods=['POST'])
@login_required
def event_register(event_id):
    event=db.get_or_404(CampusEvent,event_id)
    existing=EventRegistration.query.filter_by(event_id=event.id,user_id=current_user.id).first()
    if existing:
        db.session.delete(existing); flash('Registration cancelled.','info')
    else:
        db.session.add(EventRegistration(event_id=event.id,user_id=current_user.id))
        flash('You are registered for this event!','success')
    db.session.commit()
    return redirect(url_for('campus.events'))

@campus.route('/events/<int:event_id>/delete',methods=['POST'])
@login_required
def event_delete(event_id):
    event=db.get_or_404(CampusEvent,event_id)
    if event.created_by != current_user.id: abort(403)
    EventRegistration.query.filter_by(event_id=event.id).delete()
    db.session.delete(event); db.session.commit()
    flash('Event deleted.','success')
    return redirect(url_for('campus.events'))

@campus.route('/clubs/new',methods=['POST'])
@login_required
def club_new():
    name=request.form.get('name','').strip()
    description=request.form.get('description','').strip()
    if not name or len(name)>120:
        flash('Club name is required (max 120 characters).','danger')
    elif CampusClub.query.filter(db.func.lower(CampusClub.name)==name.lower()).first():
        flash('A club with that name already exists.','warning')
    else:
        club=CampusClub(name=name,description=description,created_by=current_user.id)
        db.session.add(club); db.session.flush()
        db.session.add(ClubMembership(club_id=club.id,user_id=current_user.id))
        db.session.commit(); flash('Club created!','success')
    return redirect(url_for('campus.events'))

@campus.route('/clubs/<int:club_id>/join',methods=['POST'])
@login_required
def club_join(club_id):
    club=db.get_or_404(CampusClub,club_id)
    member=ClubMembership.query.filter_by(club_id=club.id,user_id=current_user.id).first()
    if member:
        db.session.delete(member); flash('You left the club.','info')
    else:
        db.session.add(ClubMembership(club_id=club.id,user_id=current_user.id))
        flash('You joined the club!','success')
    db.session.commit()
    return redirect(url_for('campus.events'))

@campus.route('/marketplace')
def marketplace():
    q=request.args.get('q','').strip()
    query=MarketplaceListing.query
    if q:
        like=f'%{q}%'
        query=query.filter(db.or_(MarketplaceListing.title.ilike(like),
                                  MarketplaceListing.category.ilike(like),
                                  MarketplaceListing.description.ilike(like)))
    listings=query.order_by(MarketplaceListing.created_at.desc()).all()
    return render_template('campus/marketplace.html',listings=listings,q=q)

@campus.route('/marketplace/new',methods=['GET','POST'])
@login_required
def marketplace_new():
    if request.method=='POST':
        title=request.form.get('title','').strip()
        category=request.form.get('category','').strip()
        description=request.form.get('description','').strip()
        try:
            price=Decimal(request.form.get('price','0').strip())
            if price < 0 or price > Decimal('99999999.99'): raise InvalidOperation()
        except (InvalidOperation,ValueError):
            price=None
        if not title or len(title)>140 or not category or len(category)>80 or price is None:
            flash('Enter a valid title, category and non-negative price.','danger')
        else:
            image, _=upload_file('photo',IMAGE_EXT,'market')
            if image is False:
                flash('Photo must be PNG, JPG, WEBP or GIF.','danger')
            else:
                db.session.add(MarketplaceListing(title=title,category=category,
                    description=description,price=price,image_filename=image,user_id=current_user.id))
                db.session.commit(); flash('Marketplace listing published!','success')
                return redirect(url_for('campus.marketplace'))
    return render_template('campus/market_form.html')

@campus.route('/marketplace/<int:listing_id>/status',methods=['POST'])
@login_required
def marketplace_status(listing_id):
    listing=db.get_or_404(MarketplaceListing,listing_id)
    if listing.user_id != current_user.id: abort(403)
    status=request.form.get('status')
    if status not in ('available','sold'): abort(400)
    listing.status=status; db.session.commit()
    flash('Listing updated.','success')
    return redirect(url_for('campus.marketplace'))

@campus.route('/marketplace/<int:listing_id>/delete',methods=['POST'])
@login_required
def marketplace_delete(listing_id):
    listing=db.get_or_404(MarketplaceListing,listing_id)
    if listing.user_id != current_user.id: abort(403)
    if listing.image_filename:
        path=os.path.join(current_app.config['UPLOAD_FOLDER'],listing.image_filename)
        if os.path.exists(path): os.remove(path)
    db.session.delete(listing); db.session.commit()
    flash('Listing deleted.','success')
    return redirect(url_for('campus.marketplace'))

@campus.route('/feedback')
def feedback():
    polls=CampusPoll.query.order_by(CampusPoll.created_at.desc()).all()
    voted={v.poll_id for v in PollVote.query.filter_by(user_id=current_user.id).all()} if current_user.is_authenticated else set()
    return render_template('campus/feedback.html',polls=polls,voted=voted,
        feedback_items=CampusFeedback.query.filter_by(user_id=current_user.id).order_by(CampusFeedback.created_at.desc()).all() if current_user.is_authenticated else [])

@campus.route('/feedback/polls/new',methods=['GET','POST'])
@login_required
def poll_new():
    if request.method=='POST':
        question=request.form.get('question','').strip()
        options=[x.strip() for x in request.form.get('options','').splitlines() if x.strip()]
        if not question or len(question)>240 or len(options)<2 or len(options)>10 or len(set(x.casefold() for x in options))!=len(options) or any(len(x)>240 for x in options):
            flash('Enter a question and 2–10 unique options (one per line).','danger')
        else:
            db.session.add(CampusPoll(question=question,options_text='\\n'.join(options),created_by=current_user.id))
            db.session.commit(); flash('Poll created!','success')
            return redirect(url_for('campus.feedback'))
    return render_template('campus/poll_form.html')

@campus.route('/feedback/polls/<int:poll_id>/vote',methods=['POST'])
@login_required
def poll_vote(poll_id):
    poll=db.get_or_404(CampusPoll,poll_id)
    option=request.form.get('option','')
    if not poll.is_open:
        flash('This poll is closed.','warning')
    elif option not in poll.options:
        flash('Choose a valid option.','danger')
    elif PollVote.query.filter_by(poll_id=poll.id,user_id=current_user.id).first():
        flash('You have already voted in this poll.','info')
    else:
        db.session.add(PollVote(poll_id=poll.id,user_id=current_user.id,option_text=option))
        db.session.commit(); flash('Your vote has been counted!','success')
    return redirect(url_for('campus.feedback'))

@campus.route('/feedback/polls/<int:poll_id>/close',methods=['POST'])
@login_required
def poll_close(poll_id):
    poll=db.get_or_404(CampusPoll,poll_id)
    if poll.created_by != current_user.id: abort(403)
    poll.is_open=False; db.session.commit()
    flash('Poll closed.','success')
    return redirect(url_for('campus.feedback'))

@campus.route('/feedback/submit',methods=['POST'])
@login_required
def feedback_submit():
    category=request.form.get('category','').strip()
    message=request.form.get('message','').strip()
    anonymous=request.form.get('anonymous')=='on'
    if category not in ('Facilities','Teaching & Learning','Events','Safety','Other') or not message or len(message)>4000:
        flash('Choose a feedback category and enter a message (max 4000 characters).','danger')
    else:
        db.session.add(CampusFeedback(category=category,message=message,is_anonymous=anonymous,
                                      user_id=None if anonymous else current_user.id))
        db.session.commit(); flash('Feedback submitted. Thank you!','success')
    return redirect(url_for('campus.feedback'))

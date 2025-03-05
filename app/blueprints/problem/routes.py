"""
Routes for personal and team notes management.
"""
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.blueprints.note import bp
from app.models.user import User
from app.models.team import Team
from app.models.note import PersonalNote, TeamNote
from app.forms.note import PersonalNoteForm, TeamNoteForm, TeamForm
from app.utils.project import get_user_teams


# Personal Notes Routes
@bp.route('/notes/personal', methods=['GET'])
@login_required
def personal_notes():
    """View personal notes"""
    notes = PersonalNote.query.filter_by(user_id=current_user.id).order_by(PersonalNote.updated_at.desc()).all()
    form = PersonalNoteForm()
    return render_template('personal_notes.html', notes=notes, form=form)


@bp.route('/notes/personal/add', methods=['POST'])
@login_required
def add_personal_note():
    """Add a new personal note"""
    form = PersonalNoteForm()
    if form.validate_on_submit():
        note = PersonalNote(
            user_id=current_user.id,
            title=form.title.data,
            content=form.content.data,
            color=form.color.data
        )
        db.session.add(note)
        db.session.commit()
        flash('Note added successfully', 'success')
    return redirect(url_for('note.personal_notes'))


@bp.route('/notes/personal/<int:note_id>/edit', methods=['POST'])
@login_required
def update_personal_note(note_id):
    """Update an existing personal note"""
    note = PersonalNote.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        abort(403)

    form = PersonalNoteForm()
    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data
        note.color = form.color.data
        note.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Note updated successfully', 'success')
    return redirect(url_for('note.personal_notes'))


@bp.route('/notes/personal/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_personal_note(note_id):
    """Delete a personal note"""
    note = PersonalNote.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        abort(403)

    db.session.delete(note)
    db.session.commit()
    flash('Note deleted successfully', 'success')
    return redirect(url_for('note.personal_notes'))


# Team Notes Routes
@bp.route('/notes/team', methods=['GET'])
@login_required
def team_notes():
    """View team notes"""
    user_teams = get_user_teams()
    team_ids = [team.id for team in user_teams]
    notes = TeamNote.query.filter(TeamNote.team_id.in_(team_ids)).order_by(TeamNote.updated_at.desc()).all()

    form = TeamNoteForm()
    form.team_id.choices = [(team.id, team.name) for team in user_teams]

    return render_template('team_notes.html', notes=notes, form=form, teams=user_teams)


@bp.route('/notes/team/add', methods=['POST'])
@login_required
def add_team_note():
    """Add a new team note"""
    user_teams = get_user_teams()
    form = TeamNoteForm()
    form.team_id.choices = [(team.id, team.name) for team in user_teams]

    if form.validate_on_submit():
        # Verify the team belongs to the user
        if any(team.id == form.team_id.data for team in user_teams):
            note = TeamNote(
                team_id=form.team_id.data,
                user_id=current_user.id,
                title=form.title.data,
                content=form.content.data,
                color=form.color.data
            )
            db.session.add(note)
            db.session.commit()
            flash('Team note added successfully', 'success')
        else:
            flash('You are not a member of this team', 'danger')
    return redirect(url_for('note.team_notes'))


@bp.route('/notes/team/<int:note_id>/edit', methods=['POST'])
@login_required
def update_team_note(note_id):
    """Update an existing team note"""
    note = TeamNote.query.get_or_404(note_id)

    # Only the creator or a team member can edit
    user_teams = get_user_teams()
    team_ids = [team.id for team in user_teams]

    if note.user_id != current_user.id and note.team_id not in team_ids:
        abort(403)

    form = TeamNoteForm()
    form.team_id.choices = [(team.id, team.name) for team in user_teams]

    if form.validate_on_submit():
        # Only the owner can change the team
        if note.user_id == current_user.id:
            if any(team.id == form.team_id.data for team in user_teams):
                note.team_id = form.team_id.data
            else:
                flash('You are not a member of this team', 'danger')
                return redirect(url_for('note.team_notes'))

        note.title = form.title.data
        note.content = form.content.data
        note.color = form.color.data
        note.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Team note updated successfully', 'success')
    return redirect(url_for('note.team_notes'))


@bp.route('/notes/team/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_team_note(note_id):
    """Delete a team note"""
    note = TeamNote.query.get_or_404(note_id)

    # Only the creator can delete
    if note.user_id != current_user.id:
        abort(403)

    db.session.delete(note)
    db.session.commit()
    flash('Team note deleted successfully', 'success')
    return redirect(url_for('note.team_notes'))


# API Routes for Notes
@bp.route('/api/notes/personal', methods=['GET'])
@login_required
def api_get_personal_notes():
    """API endpoint to get personal notes"""
    notes = PersonalNote.query.filter_by(user_id=current_user.id).order_by(PersonalNote.updated_at.desc()).all()

    notes_data = [{
        'id': note.id,
        'title': note.title,
        'content': note.content,
        'color': note.color,
        'created_at': note.created_at.strftime('%Y-%m-%d %H:%M'),
        'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M')
    } for note in notes]

    return jsonify(notes_data)


@bp.route('/api/notes/personal', methods=['POST'])
@login_required
def api_add_personal_note():
    """API endpoint to add a personal note"""
    data = request.json

    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    note = PersonalNote(
        user_id=current_user.id,
        title=data['title'],
        content=data['content'],
        color=data.get('color', 'yellow')
    )

    db.session.add(note)
    db.session.commit()

    return jsonify({
        'success': True,
        'note': {
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'color': note.color,
            'created_at': note.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M')
        }
    })


@bp.route('/api/notes/personal/<int:note_id>', methods=['PUT'])
@login_required
def api_update_personal_note(note_id):
    """API endpoint to update a personal note"""
    note = PersonalNote.query.get_or_404(note_id)

    if note.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Not authorized'}), 403

    data = request.json

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    if 'title' in data:
        note.title = data['title']

    if 'content' in data:
        note.content = data['content']

    if 'color' in data:
        note.color = data['color']

    note.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'success': True,
        'note': {
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'color': note.color,
            'created_at': note.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M')
        }
    })


@bp.route('/api/notes/personal/<int:note_id>', methods=['DELETE'])
@login_required
def api_delete_personal_note(note_id):
    """API endpoint to delete a personal note"""
    note = PersonalNote.query.get_or_404(note_id)

    if note.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Not authorized'}), 403

    db.session.delete(note)
    db.session.commit()

    return jsonify({'success': True})


@bp.route('/api/notes/team', methods=['GET'])
@login_required
def api_get_team_notes():
    """API endpoint to get team notes"""
    user_teams = get_user_teams()
    team_ids = [team.id for team in user_teams]

    notes = TeamNote.query.filter(TeamNote.team_id.in_(team_ids)).order_by(TeamNote.updated_at.desc()).all()

    notes_data = [{
        'id': note.id,
        'team_id': note.team_id,
        'team_name': Team.query.get(note.team_id).name,
        'user_id': note.user_id,
        'user_name': User.query.get(note.user_id).username,
        'title': note.title,
        'content': note.content,
        'color': note.color,
        'created_at': note.created_at.strftime('%Y-%m-%d %H:%M'),
        'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M')
    } for note in notes]

    return jsonify(notes_data)


@bp.route('/api/notes/team', methods=['POST'])
@login_required
def api_add_team_note():
    """API endpoint to add a team note"""
    data = request.json

    if not data or 'title' not in data or 'content' not in data or 'team_id' not in data:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    # Verify the team belongs to the user
    user_teams = get_user_teams()
    team_ids = [team.id for team in user_teams]

    if data['team_id'] not in team_ids:
        return jsonify({'success': False, 'message': 'Not a member of this team'}), 403

    note = TeamNote(
        team_id=data['team_id'],
        user_id=current_user.id,
        title=data['title'],
        content=data['content'],
        color=data.get('color', 'blue')
    )

    db.session.add(note)
    db.session.commit()

    return jsonify({
        'success': True,
        'note': {
            'id': note.id,
            'team_id': note.team_id,
            'team_name': Team.query.get(note.team_id).name,
            'user_id': note.user_id,
            'user_name': current_user.username,
            'title': note.title,
            'content': note.content,
            'color': note.color,
            'created_at': note.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M')
        }
    })


@bp.route('/api/notes/team/<int:note_id>', methods=['PUT'])
@login_required
def api_update_team_note(note_id):
    """API endpoint to update a team note"""
    note = TeamNote.query.get_or_404(note_id)

    # Only the creator or a team member can edit
    user_teams = get_user_teams()
    team_ids = [team.id for team in user_teams]

    if note.user_id != current_user.id and note.team_id not in team_ids:
        return jsonify({'success': False, 'message': 'Not authorized'}), 403

    data = request.json

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    # Only the owner can change the team
    if 'team_id' in data and note.user_id == current_user.id:
        if data['team_id'] in team_ids:
            note.team_id = data['team_id']
        else:
            return jsonify({'success': False, 'message': 'Not a member of this team'}), 403

    if 'title' in data:
        note.title = data['title']

    if 'content' in data:
        note.content = data['content']

    if 'color' in data:
        note.color = data['color']

    note.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'success': True,
        'note': {
            'id': note.id,
            'team_id': note.team_id,
            'team_name': Team.query.get(note.team_id).name,
            'user_id': note.user_id,
            'user_name': User.query.get(note.user_id).username,
            'title': note.title,
            'content': note.content,
            'color': note.color,
            'created_at': note.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M')
        }
    })


@bp.route('/api/notes/team/<int:note_id>', methods=['DELETE'])
@login_required
def api_delete_team_note(note_id):
    """API endpoint to delete a team note"""
    note = TeamNote.query.get_or_404(note_id)

    if note.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Not authorized'}), 403

    db.session.delete(note)
    db.session.commit()

    return jsonify({'success': True})
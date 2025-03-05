"""
Routes for document management functionality.
"""
from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.blueprints.document import bp
from app.models.project import Project, ProjectDocument
from app.forms.project import ProjectDocumentForm


@bp.route('/project/<int:project_id>/documents')
@login_required
def project_documents(project_id):
    """List documents for a project"""
    project = Project.query.get_or_404(project_id)
    documents = ProjectDocument.query.filter_by(project_id=project_id).order_by(ProjectDocument.updated_at.desc()).all()
    return render_template('project_documents.html', project=project, documents=documents, project_id=project_id)


@bp.route('/project/<int:project_id>/documents/<int:doc_id>')
@login_required
def view_project_document(project_id, doc_id):
    """View a specific document"""
    project = Project.query.get_or_404(project_id)
    document = ProjectDocument.query.get_or_404(doc_id)

    # Verify the document belongs to the project
    if document.project_id != project_id:
        abort(404)

    return render_template('view_project_document.html', project=project, document=document, project_id=project_id)


@bp.route('/project/<int:project_id>/documents/new', methods=['GET', 'POST'])
@login_required
def new_project_document(project_id):
    """Create a new document"""
    project = Project.query.get_or_404(project_id)
    form = ProjectDocumentForm()

    if form.validate_on_submit():
        document = ProjectDocument(
            project_id=project_id,
            title=form.title.data,
            content=form.content.data,
            created_by_id=current_user.id,
            updated_by_id=current_user.id
        )

        db.session.add(document)
        db.session.commit()

        flash('Document created successfully', 'success')
        return redirect(url_for('document.project_documents', project_id=project_id))

    return render_template('edit_project_document.html', form=form, project=project, project_id=project_id,
                           document=None)


@bp.route('/project/<int:project_id>/documents/<int:doc_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project_document(project_id, doc_id):
    """Edit an existing document"""
    project = Project.query.get_or_404(project_id)
    document = ProjectDocument.query.get_or_404(doc_id)

    # Verify the document belongs to the project
    if document.project_id != project_id:
        abort(404)

    form = ProjectDocumentForm(obj=document)

    if form.validate_on_submit():
        document.title = form.title.data
        document.content = form.content.data
        document.updated_by_id = current_user.id

        db.session.commit()

        flash('Document updated successfully', 'success')
        return redirect(url_for('document.view_project_document', project_id=project_id, doc_id=document.id))

    return render_template('edit_project_document.html', form=form, project=project, document=document,
                           project_id=project_id)


@bp.route('/project/<int:project_id>/documents/<int:doc_id>/delete', methods=['POST'])
@login_required
def delete_project_document(project_id, doc_id):
    """Delete a document"""
    document = ProjectDocument.query.get_or_404(doc_id)

    # Verify the document belongs to the project
    if document.project_id != project_id:
        abort(404)

    db.session.delete(document)
    db.session.commit()

    flash('Document deleted successfully', 'success')
    return redirect(url_for('document.project_documents', project_id=project_id))
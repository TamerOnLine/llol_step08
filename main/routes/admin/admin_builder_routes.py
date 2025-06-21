from flask import Blueprint, render_template, request, redirect, url_for, flash
from main.models.models import db, ResumeSection
from main.extensions import db

from main.i18n_runtime import get_locale
from flask_babel import force_locale, gettext as _

from . import admin_bp


# ✅ عرض واجهة بناء السيرة
@admin_bp.route("/admin/resume_builder")
def resume_builder():
    sections = ResumeSection.query.order_by(ResumeSection.order).all()
    with force_locale(get_locale()):
        return render_template("admin/resume_builder.html.j2", sections=sections)


# ✅ إضافة قسم جديد
@admin_bp.route("/admin/resume_section/add", methods=["POST"])
def add_resume_section():
    title = request.form.get("title")
    lang = request.form.get("lang", "en")
    order = int(request.form.get("order", 0))
    section = ResumeSection(title=title, lang=lang, order=order)
    db.session.add(section)
    db.session.commit()
    with force_locale(get_locale()):
        flash(_("✅ Section added successfully"), "success")
    return redirect(url_for("admin.resume_builder"))


# ✅ تعديل قسم
@admin_bp.route("/admin/resume_section/edit/<int:section_id>", methods=["POST"])
def edit_resume_section(section_id):
    section = ResumeSection.query.get_or_404(section_id)
    new_title = request.form.get("title", section.title)

    if not new_title.strip():
        with force_locale(get_locale()):
            flash(_("⚠️ Section title cannot be empty"), "warning")
        return redirect(url_for("admin.resume_builder"))

    section.title = new_title
    section.lang = request.form.get("lang", section.lang)
    section.order = int(request.form.get("order", section.order))
    db.session.commit()

    with force_locale(get_locale()):
        flash(_("💾 Section updated successfully"), "success")
    return redirect(url_for("admin.resume_builder"))



# ✅ حذف قسم
@admin_bp.route("/admin/resume_section/delete/<int:section_id>", methods=["POST"])
def delete_resume_section(section_id):
    section = ResumeSection.query.get_or_404(section_id)
    db.session.delete(section)
    db.session.commit()
    with force_locale(get_locale()):
        flash(_("🗑️ Section deleted"), "danger")


    return redirect(url_for("admin.resume_builder"))


# ✅ تحريك قسم لأعلى
@admin_bp.route("/admin/resume_section/move_up/<int:section_id>", methods=["POST"])
def move_section_up(section_id):
    section = ResumeSection.query.get_or_404(section_id)
    previous = (
        ResumeSection.query.filter(ResumeSection.order < section.order)
        .order_by(ResumeSection.order.desc())
        .first()
    )
    with force_locale(get_locale()):
        if previous:
            section.order, previous.order = previous.order, section.order
            db.session.commit()
            flash(_("⬆️ Section moved up"), "info")
        else:
            flash(_("⚠️ Already at the top"), "warning")
    return redirect(url_for("admin.resume_builder"))


# ✅ تحريك قسم لأسفل
@admin_bp.route("/admin/resume_section/move_down/<int:section_id>", methods=["POST"])
def move_section_down(section_id):
    section = ResumeSection.query.get_or_404(section_id)
    next_item = (
        ResumeSection.query.filter(ResumeSection.order > section.order)
        .order_by(ResumeSection.order.asc())
        .first()
    )
    with force_locale(get_locale()):
        if next_item:
            section.order, next_item.order = next_item.order, section.order
            db.session.commit()
            flash(_("⬇️ Section moved down"), "info")
        else:
            flash(_("⚠️ Already at the bottom"), "warning")
    return redirect(url_for("admin.resume_builder"))


# ✅ إظهار/إخفاء قسم
@admin_bp.route(
    "/admin/resume_section/toggle_visibility/<int:section_id>", methods=["POST"]
)
def toggle_visibility(section_id):
    section = ResumeSection.query.get_or_404(section_id)
    section.is_visible = not section.is_visible
    db.session.commit()
    with force_locale(get_locale()):
        if section.is_visible:
            flash(_("👁️ Section is now visible"), "success")
        else:
            flash(_("🙈 Section is now hidden"), "warning")
    return redirect(url_for("admin.resume_builder"))

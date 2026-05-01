from flask import Blueprint, render_template

main_bp: Blueprint = Blueprint(name="main", import_name=__name__)


@main_bp.route(rule="/")
def index() -> str:
    return render_template(
        template_name_or_list="base.html", page_title="Home"
    )


@main_bp.route(rule="/health")
def health() -> tuple[str, int]:
    return "OK", 200

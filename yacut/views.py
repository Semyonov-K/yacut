import random
import string

from flask import flash, redirect, render_template, url_for

from . import app, db
from .forms import URLMapForm
from .models import URLMap

LENGTH = 6


def get_unique_short_id():
    letters_and_digits = string.ascii_letters + string.digits
    rand_string = ''.join(random.sample(letters_and_digits, LENGTH))
    if URLMap.query.filter_by(short=rand_string).first():
        get_unique_short_id()
    return rand_string


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()
    if form.validate_on_submit():
        short = form.custom_id.data or get_unique_short_id()
        url_map = URLMap(
            original=form.original_link.data,
            short=short
        )
        db.session.add(url_map)
        db.session.commit()
        flash(url_for('redirect_to_site', short=short, _external=True))
    return render_template('url_map.html', form=form)


@app.route('/<string:short>')
def redirect_to_site(short):
    return redirect(
        URLMap.query.filter_by(short=short).first_or_404().original)

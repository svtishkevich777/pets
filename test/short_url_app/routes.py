import string

from my_project_1.models import Link, db, app
from flask import render_template, request, redirect, url_for, flash
from random import choices
from typing import Optional

CHARACTERS = string.digits + string.ascii_letters


def generate_random_short_url():
    return ''.join(choices(CHARACTERS, k=4))


@app.template_filter('trimmer')
def trimmer_filter(s):
    if len(s) > 50:
        return s[:50] + '...'
    return s


def get_link_by_long_url_or_none(long_url) -> Optional[Link]:
    return Link.query.filter_by(long_url=long_url).first()


def get_link_by_short_url_or_none(short_url) -> Optional[Link]:
    return Link.query.filter_by(short_url=short_url).first()


def get_link_by_long_url() -> Link:
    link = Link.query.filter_by(long_url=request.form['long_url']).first()
    if link is None:
        raise Exception
    return link


@app.route('/', methods=['POST', 'GET'])
def new_url():
    if request.method == 'GET':
        data = Link.query.all()
        return render_template('super.html', datas=data, host=request.base_url)
    elif request.method == 'POST':
        if request.form['long_url']:
            repeat_long = get_link_by_long_url_or_none(request.form['long_url'])
            if repeat_long:
                flash('This link has already been used, please add a new one!', category='error')
            else:
                if len(request.form['short_url']) >= 4:
                    repeat_short = get_link_by_short_url_or_none(request.form['short_url'])
                    if repeat_short:
                        flash('This link already exists', category='already')
                    else:
                        flash('You have created your link', category='created')
                        link = Link(long_url=request.form['long_url'], short_url=request.form['short_url'])
                        link.save()
                else:
                    flash('The link was generated automatically', category='generated')
                    short_url = generate_random_short_url()
                    link = Link(long_url=request.form['long_url'], short_url=short_url)
                    link.save()
    return redirect(url_for('new_url'))


@app.route('/<short_url>')
def redirect_to_url(short_url):
    link = Link.query.filter_by(short_url=short_url).first()
    link.visits = link.visits + 1
    db.session.commit()
    return redirect(link.long_url)


@app.route('/delete')
def delete():
    db.session.query(Link).filter_by(id=request.args.get('id')).delete()
    db.session.commit()
    return redirect(url_for('new_url'))


if __name__ == '__main__':
    app.run()

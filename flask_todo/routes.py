from flask_todo.models import Todo, User, app
from flask import render_template, request, redirect, url_for, flash
from flask_todo.utils import get_data, get_move_in_front_data, get_move_back_data,\
    Nodata, find_next_traffic, get_user_email_password, NoUserPassword, check_user_name_email, get_user, get_user_filter
from flask_todo.forms import LoginForm, RegisterForm
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash


@app.route('/', methods=['POST', 'GET'])
@login_required
def table_todo():
    if request.method == 'GET':
        data = get_user(current_user.id)
        return render_template('home_table.html', datas=data, user=current_user)
    else:
        flash('Task created', category='new_task')
        traffic = find_next_traffic()
        data = Todo(task=request.form['task'],
                    status=request.form['status'],
                    traffic=traffic,
                    user=current_user)
        data.save()
        return redirect(url_for('table_todo',
                                status=request.args.get('status'), user=current_user))


@app.route('/up/<display>', methods=['POST'])
@login_required
def move_in_front(display):
    data = get_data(display)
    try:
        data_next = get_move_in_front_data(data, current_user)
    except Nodata:
        return redirect(url_for('table_todo', user=current_user))
    data.traffic, data_next.traffic = \
        data_next.traffic, data.traffic
    data.save()
    data_next.save()
    return redirect(url_for('table_todo', user=current_user))


@app.route('/down/<display>', methods=['POST'])
@login_required
def move_back(display):
    data = get_data(display)
    try:
        data_next = get_move_back_data(data, current_user)
    except Nodata:
        return redirect(url_for('table_todo', user=current_user))
    data.traffic, data_next.traffic = \
        data_next.traffic, data.traffic
    data.save()
    data_next.save()
    return redirect(url_for('table_todo', user=current_user))


@app.route('/filter/<status>', methods=['POST', 'GET'])
@login_required
def table_filter(status):
    if request.method == 'GET':
        data = get_user_filter(current_user.id, status=status)
        return render_template('double.html', datas=data, status=status, user=current_user)
    else:
        return redirect(url_for('table_todo', user=current_user))


@app.route('/done/<pk>', methods=['POST'])
@login_required
def done(pk):
    data = Todo.query.filter_by(id=pk).first()
    data.done = not data.done
    data.save()
    return redirect(url_for('table_todo', user=current_user))


@app.route('/update/<pk>', methods=['POST', 'GET'])
@login_required
def update(pk):
    obj = Todo.query.filter_by(id=pk).first()
    if request.method == 'GET':
        return render_template('update.html', obj=obj, id=pk, user=current_user)
    else:
        obj.task = request.form['task']
        obj.save()
        return redirect(url_for('table_todo', user=current_user))


@app.route('/new_status/<pk>', methods=['POST', 'GET'])
@login_required
def update_status(pk):
    if request.method == 'GET':
        return render_template('update_status.html', id=pk, user=current_user)
    else:
        data = Todo.query.filter_by(id=pk).first()
        data.status = request.form['status']
        data.save()
        return redirect(url_for('table_todo', user=current_user))


@app.route('/delete/<pk>')
@login_required
def delete(pk):
    flash('Task delete', category='task_delete')
    data = Todo.query.filter_by(id=pk).first()
    data.delete()
    return redirect(url_for('table_todo', user=current_user))


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html', form=form, user=current_user)
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        try:
            user = get_user_email_password(email, password)
        except NoUserPassword:
            return render_template('login.html', form=form, user=current_user)
        login_user(user, remember=form.remember.data)
        return redirect(url_for('table_todo', user=current_user))
    return render_template('login.html', form=form, user=current_user)


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if request.method == 'GET':
        return render_template('register.html', form=form, user=current_user)
    if form.validate_on_submit():
        name = form.username.data
        email = form.email.data
        if check_user_name_email(name, email):
            return render_template('register.html', form=form, user=current_user)
        password = generate_password_hash(form.password.data)
        user = User(name=name, email=email, password=password)
        user.save()
        return redirect(url_for('login', user=current_user))
    return render_template('register.html', form=form, user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('table_todo', user=current_user))


if __name__ == '__main__':
    app.run()

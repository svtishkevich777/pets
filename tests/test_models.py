from flask_todo.models import Todo, User, app, db
from werkzeug.security import generate_password_hash
from flask import url_for
from flask_testing import TestCase
from unittest.mock import patch, MagicMock
from flask_todo.utils import Nodata, NoUserPassword
import unittest


class ModelTestCase(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        user = User(name='Sergey',
                    email='user@email.com',
                    password=generate_password_hash('123asd'))
        db.session.add(user)
        db.session.add(Todo(task='task one',
                            status='urgent',
                            traffic=1,
                            user=user))
        db.session.add(Todo(task='task two',
                            status='not urgent',
                            traffic=2,
                            user=user))

        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @patch('flask_todo.routes.get_user')
    @patch('flask_todo.routes.current_user')
    def test_table_todo(self, mock_current_user, mock_get_user):
        app.config['LOGIN_DISABLED'] = True
        mock1 = MagicMock()
        mock_get_user.return_value = [mock1]
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('home_table.html')
        self.assertEqual(self.get_context_variable('datas'), [mock1])
        self.assertEqual(self.get_context_variable('user'), mock_current_user)

    @patch('flask_todo.routes.find_next_traffic')
    @patch('flask_todo.routes.current_user')
    @patch('flask_todo.routes.Todo')
    @patch('flask_todo.routes.flash')
    def test_read_post_data(self, mock_flash, mock_Todo, mock_current_user, mock_find_next_traffic):
        app.config['LOGIN_DISABLED'] = True
        mock_find_next_traffic.return_value = 3
        data = {'task': 'task one', 'status': 'status'}
        response = self.client.post('/', data=data, query_string={'status': 'urgent'})
        mock_Todo.assert_called_once_with(task=data['task'], status=data['status'], traffic=3, user=mock_current_user)
        mock_flash.assert_called_once_with('Task created', category='new_task')
        mock_find_next_traffic.assert_called_once()
        mock_Todo().save.assert_called_once()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url_for('table_todo', status='urgent', user=mock_current_user))

    @patch('flask_todo.routes.current_user')
    @patch('flask_todo.routes.get_data')
    @patch('flask_todo.routes.get_move_in_front_data')
    def test_move_in_front(self, mock_get_move_in_front_data, mock_get_data, mock_current_user):
        app.config['LOGIN_DISABLED'] = True
        mock1 = MagicMock()
        mock_get_data.return_value = mock1
        mock_get_move_in_front_data.side_effect = Nodata
        response = self.client.post('/up/2')
        self.assertRedirects(response, url_for('table_todo', user=mock_current_user))
        mock_get_data.assert_called_once_with('2')
        mock_get_move_in_front_data.assert_called_once_with(mock1, mock_current_user)

    @patch('flask_todo.routes.current_user')
    @patch('flask_todo.routes.get_data')
    @patch('flask_todo.routes.get_move_in_front_data')
    def test_move_in_front_try(self, mock_get_move_in_front_data, mock_get_data, mock_current_user):
        app.config['LOGIN_DISABLED'] = True
        mock1 = MagicMock(traffic=1)
        mock2 = MagicMock(traffic=2)
        mock_get_data.return_value = mock1
        mock_get_move_in_front_data.return_value = mock2
        response = self.client.post('/up/3')
        self.assertRedirects(response, url_for('table_todo', user=mock_current_user))
        mock_get_data.assert_called_once_with('3')
        mock_get_move_in_front_data.assert_called_once_with(mock1, mock_current_user)
        mock_get_data().save.assert_called_once()
        mock_get_move_in_front_data().save.assert_called_once()
        self.assertEqual(mock1.traffic, 2)
        self.assertEqual(mock2.traffic, 1)

    @patch('flask_todo.routes.current_user')
    @patch('flask_todo.routes.get_data')
    @patch('flask_todo.routes.get_move_back_data')
    def test_move_back(self, mock_get_move_back_data, mock_get_data, mock_current_user):
        app.config['LOGIN_DISABLED'] = True
        mock1 = MagicMock()
        mock_get_data.return_value = mock1
        mock_get_move_back_data.side_effect = Nodata
        response = self.client.post('/down/1')
        self.assertRedirects(response, url_for('table_todo', user=mock_current_user))
        mock_get_data.assert_called_once_with('1')
        mock_get_move_back_data.assert_called_once_with(mock1, mock_current_user)

    @patch('flask_todo.routes.current_user')
    @patch('flask_todo.routes.get_data')
    @patch('flask_todo.routes.get_move_back_data')
    def test_move_back_try(self, mock_get_move_back_data, mock_get_data, mock_current_user):
        app.config['LOGIN_DISABLED'] = True
        mock1 = MagicMock(traffic=1)
        mock2 = MagicMock(traffic=2)
        mock_get_data.return_value = mock1
        mock_get_move_back_data.return_value = mock2
        response = self.client.post('/down/3')
        self.assertRedirects(response, url_for('table_todo', user=mock_current_user))
        mock_get_data.assert_called_once_with('3')
        mock_get_move_back_data.assert_called_once_with(mock1, mock_current_user)
        mock_get_data().save.assert_called_once()
        mock_get_move_back_data().save.assert_called_once()
        self.assertEqual(mock1.traffic, 2)
        self.assertEqual(mock2.traffic, 1)

    @patch('flask_todo.routes.get_user_filter')
    @patch('flask_todo.routes.current_user')
    def test_table_filter(self, mock_current_user, mock_get_user_filter):
        app.config['LOGIN_DISABLED'] = True
        mock1 = MagicMock()
        mock_get_user_filter.return_value = mock1
        some_status = 'not urgent'
        response = self.client.get(f'/filter/{some_status}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('double.html')
        mock_get_user_filter.assert_called_once()
        self.assertEqual(self.get_context_variable('user'), mock_current_user)
        self.assertEqual(self.get_context_variable('datas'), mock1)

    @patch('flask_todo.routes.current_user')
    def test_done_true(self, mock_current_user):
        app.config['LOGIN_DISABLED'] = True
        response = self.client.post('/done/1')
        self.assertRedirects(response, url_for('table_todo', user=mock_current_user))
        data = Todo.query.filter_by(id=1).first()
        self.assertEqual(data.done, True)

    @patch('flask_todo.routes.current_user')
    def test_update_task(self, mock_current_user):
        app.config['LOGIN_DISABLED'] = True
        data = {'task': 'task updated'}
        some_id = 1
        response = self.client.post(f'/update/{some_id}', data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url_for('table_todo', user=mock_current_user))
        data_updated = Todo.query.filter_by(id=some_id).first()
        self.assertEqual(data['task'], data_updated.task)

    @patch('flask_todo.routes.current_user')
    def test_update_status(self, mock_current_user):
        app.config['LOGIN_DISABLED'] = True
        data = {'status': 'not urgent'}
        some_id = 1
        response = self.client.post(f'/new_status/{some_id}', data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url_for('table_todo', user=mock_current_user))
        data_updated = Todo.query.filter_by(id=some_id).first()
        self.assertEqual(data['status'], data_updated.status)

    @patch('flask_todo.routes.flash')
    @patch('flask_todo.routes.current_user')
    def test_delete(self, mock_current_user, mock_flash):
        app.config['LOGIN_DISABLED'] = True
        response = self.client.get('/delete/1')
        data_del = Todo.query.all()
        mock_flash.assert_called_once_with('Task delete', category='task_delete')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url_for('table_todo', user=mock_current_user))
        self.assertEqual(len(data_del), 1)

    @patch('flask_todo.routes.LoginForm')
    @patch('flask_todo.routes.current_user')
    def test_login(self, mock_current_user, mock_login):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('login.html')
        mock_login.assert_called_once()
        self.assertEqual(self.get_context_variable('user'), mock_current_user)
        self.assertEqual(self.get_context_variable('form'), mock_login())

    @patch('flask_todo.routes.LoginForm')
    @patch('flask_todo.routes.current_user')
    def test_login_post(self, mock_current_user, mock_login):
        mock1 = MagicMock()
        mock_login.return_value = mock1
        mock1.validate_on_submit.return_value = False
        response = self.client.post('/login')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('login.html')
        mock_login.assert_called_once()
        self.assertEqual(self.get_context_variable('user'), mock_current_user)
        self.assertEqual(self.get_context_variable('form'), mock_login())

    @patch('flask_todo.routes.get_user_email_password')
    @patch('flask_todo.routes.LoginForm')
    @patch('flask_todo.routes.current_user')
    def test_login_post_true_except(self, mock_current_user, mock_login, mock_get_user):
        mock1 = MagicMock(email=MagicMock(data='mail'), password=MagicMock(data='password'))
        mock_login.return_value = mock1
        mock1.validate_on_submit.return_value = True
        mock_get_user.side_effect = NoUserPassword
        response = self.client.post('/login')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('login.html')
        mock_login.assert_called_once()
        self.assertEqual(self.get_context_variable('user'), mock_current_user)
        self.assertEqual(self.get_context_variable('form'), mock_login())

    @patch('flask_todo.routes.login_user')
    @patch('flask_todo.routes.get_user_email_password')
    @patch('flask_todo.routes.LoginForm')
    @patch('flask_todo.routes.current_user')
    def test_login_post_true_try(self, mock_current_user,
                                 mock_login, mock_get_user, mock_login_user):
        mock1 = MagicMock(email=MagicMock(data='mail'),
                          password=MagicMock(data='password'),
                          remember=MagicMock(data=True))
        mock_login.return_value = mock1
        mock1.validate_on_submit.return_value = True
        mock2 = MagicMock()
        mock_get_user.return_value = mock2
        response = self.client.post('/login')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url_for('table_todo', user=mock_current_user))
        mock_login.assert_called_once()
        mock_login_user.assert_called_once_with(mock2, remember=mock1.remember.data)

    @patch('flask_todo.routes.RegisterForm')
    @patch('flask_todo.routes.current_user')
    def test_register(self, mock_current_user, mock_register_form):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('register.html')
        mock_register_form.assert_called_once()
        self.assertEqual(self.get_context_variable('user'), mock_current_user)
        self.assertEqual(self.get_context_variable('form'), mock_register_form())

    @patch('flask_todo.routes.RegisterForm')
    @patch('flask_todo.routes.current_user')
    def test_register_post_false(self, mock_current_user, mock_register_form):
        mock1 = MagicMock()
        mock_register_form.return_value = mock1
        mock1.validate_on_submit.return_value = False
        response = self.client.post('/register')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('register.html')
        mock_register_form.assert_called_once()
        self.assertEqual(self.get_context_variable('user'), mock_current_user)
        self.assertEqual(self.get_context_variable('form'), mock_register_form())

    @patch('flask_todo.routes.check_user_name_email')
    @patch('flask_todo.routes.RegisterForm')
    @patch('flask_todo.routes.current_user')
    def test_login_post_true_exept(self, mock_current_user, mock_register_form, mock_check_user):
        mock1 = MagicMock(email=MagicMock(data='mail'), password=MagicMock(data='password'))
        mock_register_form.return_value = mock1
        mock1.validate_on_submit.return_value = True
        mock_check_user.return_value = True
        response = self.client.post('/register')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('register.html')
        mock_register_form.assert_called_once()
        self.assertEqual(self.get_context_variable('user'), mock_current_user)
        self.assertEqual(self.get_context_variable('form'), mock_register_form())


if __name__ == '__main__':
    unittest.main()

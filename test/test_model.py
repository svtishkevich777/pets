from short_url_app.routes import db, app
from short_url_app.models import Link
from flask import url_for
from unittest.mock import patch
from flask_testing import TestCase


class ModelTestCase(TestCase):
    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        return app

    def setUp(self):
        db.session.add(Link(
            long_url='http://longtest1',
            short_url='1111',
                            ))
        db.session.add(Link(
            long_url='http://longtest2',
            short_url='2222',
                            ))
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_success(self):
        response = self.client.get(url_for('new_url'))
        data = Link.query.all()
        self.assert200(response)
        self.assert_template_used('super.html')
        self.assertContext('datas', data)
        self.assertContext('host', 'http://localhost/')

    def test_post_form_long_url_false(self):
        response = self.client.post(url_for('new_url'), data={
            'long_url': '',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url_for('new_url'))

    @patch('short_url_app.routes.flash')
    def test_post_form_long_url_true_repeat_true(self, mock_flash):
        response = self.client.post(url_for('new_url'), data={
            'long_url': 'http://longtest2',
        })
        mock_flash.assert_called_once_with('This link has already been used, please add a new one!', category='error')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url_for('new_url'))

    def test_post_form_long_url_true(self):
        response = self.client.post(url_for('new_url'), data={
            'long_url': 'http://longtest3', 'short_url': '3333'
        })
        datalong = Link.query.all()
        self.assertEqual(len(datalong), 3)
        self.assertEqual(datalong[-1].long_url, 'http://longtest3')

    @patch('short_url_app.routes.flash')
    def test_post_form_short_url_true_repeat_true(self, mock_flash):
        response = self.client.post(url_for('new_url'), data={
            'long_url': 'http://longtest3', 'short_url': '1111'
        })
        mock_flash.assert_called_once_with('This link already exists', category='already')
        self.assertEqual(response.status_code, 302)

    @patch('short_url_app.routes.flash')
    def test_post_form_short_url_true(self, mock_flash):
        response = self.client.post(url_for('new_url'), data={
            'long_url': 'http://longtest3', 'short_url': '3333'
        })
        mock_flash.assert_called_once_with('You have created your link', category='created')
        datashort = Link.query.all()
        self.assertEqual(len(datashort), 3)
        self.assertEqual(datashort[-1].short_url, '3333')
        self.assertEqual(response.status_code, 302)

    @patch('short_url_app.routes.flash')
    @patch('short_url_app.routes.get_link_by_long_url_or_none')
    @patch('short_url_app.routes.Link')
    @patch('short_url_app.routes.generate_random_short_url')
    def test_post_form_short_url_generating(
            self, generate_random_short_url_patch, link_patch, get_link_by_long_url_or_none_patch, mock_flash):
        get_link_by_long_url_or_none_patch.return_value = None
        generate_random_short_url_patch.return_value = 'ABC'
        response = self.client.post(url_for('new_url'), data={
            'long_url': 'http://longtest3', 'short_url': '333'
        })
        generate_random_short_url_patch.assert_called_once()
        mock_flash.assert_called_once_with('The link was generated automatically', category='generated')
        link_patch.assert_called_once_with(long_url='http://longtest3', short_url='ABC')
        link_patch().save.assert_called_once()

    def test_visit(self):
        response = self.client.get('/1111')
        link = Link.query.filter_by(short_url='1111').first()
        self.assertEqual(link.visits, 1)
        self.assertEqual(response.status_code, 302)

    def test_delete(self):
        response = self.client.get(url_for('delete'), query_string={
            'id': 1
        })
        data_del = Link.query.all()
        self.assertEqual(len(data_del), 1)

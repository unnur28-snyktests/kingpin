import logging

from boto.exception import BotoServerError
from tornado import gen
from tornado import testing
import mock

from kingpin.actors.aws import cloudformation
from kingpin.actors.aws import settings

log = logging.getLogger(__name__)


@gen.coroutine
def tornado_value(*args):
    """Returns whatever is passed in. Used for testing."""
    raise gen.Return(*args)


class TestCreate(testing.AsyncTestCase):

    def setUp(self):
        super(TestCreate, self).setUp()
        settings.AWS_ACCESS_KEY_ID = 'unit-test'
        settings.AWS_SECRET_ACCESS_KEY = 'unit-test'

    def test_get_template_body(self):
        # Should work...
        actor = cloudformation.Create(
            'Unit Test Action',
            {'name': 'unit-test-cf',
             'region': 'us-west-2',
             'template': 'examples/test/aws.cloudformation/cf.unittest.json'})
        # TODO: Fill this in with some real content
        self.assertEquals(actor._template_body, '')
        self.assertEquals(actor._template_url, None)

        # Should return None
        actor = cloudformation.Create(
            'Unit Test Action',
            {'name': 'unit-test-cf',
             'region': 'us-west-2',
             'template': 'http://foobar.json'})
        self.assertEquals(actor._template_body, None)
        self.assertEquals(actor._template_url, 'http://foobar.json')

        # Should raise exception
        with self.assertRaises(cloudformation.InvalidTemplateException):
            actor = cloudformation.Create(
                'Unit Test Action',
                {'name': 'unit-test-cf',
                 'region': 'us-west-2',
                 'template': 'missing'})

    @testing.gen_test()
    def test_validate_template_body(self):
        actor = cloudformation.Create(
            'Unit Test Action',
            {'name': 'unit-test-cf',
             'region': 'us-west-2',
             'template': 'examples/test/aws.cloudformation/cf.unittest.json'})
        actor.conn.validate_template = mock.MagicMock()
        yield actor._validate_template()
        actor.conn.validate_template.assert_called_with(
            template_body='', template_url=None)

    @testing.gen_test()
    def test_validate_template_url(self):
        actor = cloudformation.Create(
            'Unit Test Action',
            {'name': 'unit-test-cf',
             'region': 'us-west-2',
             'template': 'http://foobar.json'})
        actor.conn.validate_template = mock.MagicMock()
        yield actor._validate_template()
        actor.conn.validate_template.assert_called_with(
            template_body=None, template_url='http://foobar.json')

    @testing.gen_test()
    def test_validate_template_raises_boto_error(self):
        actor = cloudformation.Create(
            'Unit Test Action',
            {'name': 'unit-test-cf',
             'region': 'us-west-2',
             'template': 'http://foobar.json'})
        actor.conn.validate_template = mock.MagicMock()
        actor.conn.validate_template.side_effect = BotoServerError(
            'ValidationError', 'Invalid template property or properties')

        with self.assertRaises(cloudformation.InvalidTemplateException):
            yield actor._validate_template()

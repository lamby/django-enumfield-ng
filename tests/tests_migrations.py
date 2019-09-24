import os
import shutil
import tempfile
import subprocess

from django.test import TestCase as DjangoTestCase


class MigrationIntegrationTests(DjangoTestCase):
    """
    In order to test migrations in the test project, via the public migrations
    interface (the management commands), we copy the test directory into a
    temporary location, and run management commands against that project.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        src = os.path.dirname(__file__)

        shutil.copytree(
            src,
            os.path.join(self.tmp, os.path.basename(src)),
        )

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_command(self, command, expect_failure=False):
        failed = False
        try:
            return subprocess.check_output(
                'python %s/tests/manage.py %s' % (self.tmp, command),
                shell=True,
            )
        except subprocess.CalledProcessError as e:
            if expect_failure:
                self.assertNotEqual(e.returncode, 0)
                failed = True
            else:
                self.assertEqual(e.returncode, 0)

        self.assertEqual(failed, expect_failure)

    def assertMigrationExists(self, migration_number, exists=True):
        migration_dir = os.path.join(self.tmp, 'tests', 'migrations')

        migration_numbers = [
            x.split('_')[0] for x in os.listdir(migration_dir)
        ]

        self.assertEqual(migration_number in migration_numbers, exists)

    def test_make_migrations(self):
        self.run_command('makemigrations tests')
        self.assertMigrationExists('0001')

    def test_migrate(self):
        self.run_command('makemigrations tests')
        self.assertMigrationExists('0001')
        self.run_command('migrate')

    def test_stable_migrations(self):
        self.run_command('makemigrations tests')
        self.assertMigrationExists('0001')

        self.run_command('migrate')

        self.run_command('makemigrations tests --check', expect_failure=True)

        self.assertMigrationExists('0002', exists=False)

import pytest


pytestmark = pytest.mark.usefixtures('config')


@pytest.fixture
def config(testdir):
    testdir.makeini("""
        [pytest]
        IMAGE = master
        MINION_IMAGE = minion
        TAGS = #sometag #some-other-tag
    """)


def test_nspawn_container(testdir):
    testdir.makepyfile("""
        import pytest
        from functools import partial
        from saltcontainers.factories import ContainerFactory


        def test_sth(request, salt_root, salt_master_config):
            container = ContainerFactory(
                type='nspawn',
                config__image=request.config.getini('IMAGE'),
                config__salt_config__tmpdir=salt_root,
                config__salt_config__conf_type='master',
                config__salt_config__config=salt_master_config)
            request.addfinalizer(
                partial(
                    container['config']['client'].stop,
                    container['config']['name']))
    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines(['*::test_sth PASSED'])


def test_nspawn_master_container(testdir):
    testdir.makepyfile("""
        import pytest


        @pytest.fixture(scope="module")
        def master_container_extras():
            return dict(type='nspawn')


        def test_sth(master_container):
            assert master_container['ip']
    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines(['*::test_sth PASSED'])


def test_nspawn_master(testdir):
    testdir.makepyfile("""
        import pytest


        @pytest.fixture(scope="module")
        def master_container_extras():
            return dict(type='nspawn')


        def test_sth(master):
            assert master['container']['ip']
    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines(['*::test_sth PASSED'])


def test_nspawn_minion_container(testdir):
    testdir.makepyfile("""
        import pytest


        @pytest.fixture(scope="module")
        def minion_container_extras():
            return dict(type='nspawn')


        def test_sth(minion_container):
            assert minion_container['ip']
    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines(['*::test_sth PASSED'])


def test_nspawn_minion(testdir):
    testdir.makepyfile("""
        import pytest


        @pytest.fixture(scope="module")
        def master_container_extras():
            return dict(type='nspawn')


        @pytest.fixture(scope="module")
        def minion_container_extras():
            return dict(type='nspawn')


        def test_sth(minion):
            assert minion['container']['ip']
    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines(['*::test_sth PASSED'])


def test_nspawn_master_run_stream(testdir):
    testdir.makepyfile("""
        import pytest


        @pytest.fixture(scope="module")
        def master_container_extras():
            return dict(type='nspawn')


        def test_sth(master):
            for item in master['container'].run('cat /etc/os-release', stream=True):
                if 'VERSION="12-SP2"' in item:
                    break
            else:
                assert False
    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines(['*::test_sth PASSED'])


def test_nspawn_minion_key_cached(testdir):
    testdir.makepyfile("""
        import json
        import pytest


        @pytest.fixture(scope="module")
        def master_container_extras():
            return dict(type='nspawn')


        @pytest.fixture(scope="module")
        def minion_container_extras():
            return dict(type='nspawn')


        def test_sth(master, minion, minion_key_cached):
            keys = json.loads(master['container'].run('salt-key -L'))
            assert minion['id'] in keys['Unaccepted Keys']
    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines(['*::test_sth PASSED'])


def test_nspawn_minion_key_accepted(testdir):
    testdir.makepyfile("""
        import json
        import pytest


        @pytest.fixture(scope="module")
        def master_container_extras():
            return dict(type='nspawn')


        @pytest.fixture(scope="module")
        def minion_container_extras():
            return dict(type='nspawn')


        def test_sth(master, minion, minion_key_accepted):
            keys = json.loads(master['container'].run('salt-key -L'))
            assert minion['id'] in keys['Accepted Keys']
    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines(['*::test_sth PASSED'])


def test_nspawn_minion_ping(testdir):
    testdir.makepyfile("""
        import pytest


        @pytest.fixture(scope="module")
        def master_container_extras():
            return dict(type='nspawn')


        @pytest.fixture(scope="module")
        def minion_container_extras():
            return dict(type='nspawn')


        def test_sth(master, minion, minion_key_accepted):
            assert master.salt(minion['id'], "test.ping")[minion['id']] is True
    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines(['*::test_sth PASSED'])

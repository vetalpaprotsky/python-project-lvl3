import pytest
import os
from tests.utils import load_fixture, is_content_identical
from page_loader.download import download
from page_loader.exceptions import HTTPError, DirectoryError


def test_download_page_with_resources(requests_mock, tmpdir):
    page_html = load_fixture('page.html')
    application_css_content = 'h3 { color: red; }'
    application_js_content = 'alert("Hexlet");'
    runtime_js_content = 'alert("JS");'
    python_png_binary = b'\xAB\xBC\xCD\xDE\xEF'
    page_url = 'https://ru.hexlet.io/courses'

    mocks = [
        (
            # the page itself and link href="/courses"
            page_url,
            page_html,
        ),
        (
            # link href="/assets/application.css"
            'https://ru.hexlet.io/assets/application.css',
            application_css_content,
        ),
        (
            # script src="/assets/application.js"
            'https://ru.hexlet.io/assets/application.js',
            application_js_content,
        ),
        (
            # script src="https://ru.hexlet.io/packs/js/runtime.js"
            'https://ru.hexlet.io/packs/js/runtime.js',
            runtime_js_content,
        ),
        (
            # img src="/assets/professions/python.png"
            'https://ru.hexlet.io/assets/professions/python.png',
            python_png_binary,
        ),
    ]
    for url, content in mocks:
        if isinstance(content, bytes):
            requests_mock.get(url, content=content)
        else:
            requests_mock.get(url, text=content)

    page_file_path = tmpdir / 'ru-hexlet-io-courses.html'
    assert download(page_url, str(tmpdir)) == page_file_path

    with open(page_file_path) as file:
        assert is_content_identical(
            file.read(),
            load_fixture('page_after_download.html')
        )

    resources = [
        ('ru-hexlet-io-courses.html', page_html),
        ('ru-hexlet-io-assets-application.css', application_css_content),
        ('ru-hexlet-io-assets-application.js', application_js_content),
        ('ru-hexlet-io-packs-js-runtime.js', runtime_js_content),
        ('ru-hexlet-io-assets-professions-python.png', python_png_binary),
    ]
    resources_dir_path = tmpdir / 'ru-hexlet-io-courses_files'
    for name, content in resources:
        resource_path = resources_dir_path / name
        read_mode = 'rb' if isinstance(content, bytes) else 'r'
        with open(resource_path, read_mode) as file:
            assert file.read() == content


def test_download_page_with_some_unavailable_resources(requests_mock, tmpdir):
    page_html = '''
        <html>
            <body>
                <img src="available.png">
                <img src="unavailable.png">
            <body>
        </html>
    '''
    page_url = 'http://test.com'
    requests_mock.get(page_url, text=page_html)
    requests_mock.get(page_url + '/available.png', content=b'\xFF')
    requests_mock.get(page_url + '/unavailable.png', status_code=404)

    download(page_url, str(tmpdir))

    resources_dir_path = tmpdir / 'test-com_files'
    assert os.path.isfile(tmpdir / 'test-com.html')
    assert os.path.isfile(resources_dir_path / 'test-com-available.png')
    assert not os.path.isfile(resources_dir_path / 'test-com-unavailable.png')


def test_download_page_without_resources(requests_mock, tmpdir):
    page_url = 'http://test.com'
    requests_mock.get(page_url, text='<html></html>')

    download(page_url, str(tmpdir))

    resources_dir_path = tmpdir / 'test-com_files'
    assert os.path.isfile(tmpdir / 'test-com.html')
    assert not os.path.isdir(resources_dir_path)


def test_download_unavailable_page(requests_mock, tmpdir):
    page_url = 'http://test.com'
    requests_mock.get(page_url, status_code=404)

    with pytest.raises(HTTPError):
        download(page_url, str(tmpdir))


def test_download_with_non_existing_output_dir(requests_mock):
    page_html = '''
        <html>
            <body>
                <script src="script.js"></script>
            <body>
        </html>
    '''
    page_url = 'http://test.com'
    requests_mock.get(page_url, text=page_html)
    requests_mock.get(page_url + '/script.js', text='console.log("JS");')

    with pytest.raises(DirectoryError):
        download(page_url, 'non/existing/dir/path')

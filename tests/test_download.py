import os
from tests.utils import load_fixture, whitespaces_removed
from page_loader.download import download


def test_download_page_without_resources(requests_mock, tmpdir):
    page_content = '<html></html>'
    page_url = 'http://this.is.a.test/page'
    requests_mock.get(page_url, text=page_content)

    page_path = tmpdir / 'this-is-a-test-page.html'
    assert download(page_url, str(tmpdir)) == page_path

    with open(page_path) as file:
        page = whitespaces_removed(file.read())
        expected = whitespaces_removed(page_content)
        assert page == expected

    resources_dir_path = tmpdir / 'this-is-a-test-page_files'
    assert not os.path.isdir(resources_dir_path)


def test_download_page_with_resources(requests_mock, tmpdir):
    # css_file_content = 'h1 { color: red; }'
    # js_file_content = 'alert("JS");'
    image_binary = b'\xAB\xBC\xCD\xDE\xEF'
    domain_url = 'https://ru.hexlet.io'
    page_url = domain_url + '/courses'

    requests_mock.get(
        page_url,
        text=load_fixture('hexlet_courses.html'),
    )
    # requests_mock.get(
    #     domain_url + '/assets/styles/main.css',
    #     text=css_file_content
    # )
    # requests_mock.get(
    #     domain_url + '/assets/scripts/main.js',
    #     text=js_file_content
    # )
    requests_mock.get(
        domain_url + '/assets/professions/python.png',
        content=image_binary,
    )

    page_path = tmpdir / 'ru-hexlet-io-courses.html'
    assert download(page_url, str(tmpdir)) == page_path

    with open(page_path) as file:
        # TODO: Come up with a better way to check whether pages are equal.
        page = whitespaces_removed(file.read())
        expected = whitespaces_removed(
            load_fixture('hexlet_courses_after_download.html')
        )
        assert sorted(page) == sorted(expected)

    resources_dir_path = tmpdir / 'ru-hexlet-io-courses_files'
    image_path = (
        resources_dir_path / 'ru-hexlet-io-assets-professions-python.png'
    )

    with open(image_path, 'rb') as image:
        assert image.read() == image_binary

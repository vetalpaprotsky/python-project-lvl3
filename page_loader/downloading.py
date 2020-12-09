import os
from progress.bar import Bar
from page_loader.logging import logger
from page_loader.exceptions import FileError, HTTPError
from page_loader.dom_tree import set_local_resources
from page_loader.resources import get_content
from page_loader.utils import write_to_file, create_dir
from page_loader.urls import url_to_name, url_to_file_name


def download(page_url, output_dir_path):
    page_html = get_content(page_url, decode=True)

    resources_dir_path = os.path.join(
        output_dir_path, url_to_name(page_url) + '_files',
    )
    updated_page_html, resources_info = set_local_resources(
        page_html, page_url, resources_dir_path,
    )

    page_file_path = os.path.join(output_dir_path, url_to_file_name(page_url))
    write_to_file(updated_page_html, page_file_path)

    resources_count = len(resources_info)
    if resources_count > 0:
        create_dir(resources_dir_path)
        progress_bar = Bar('Downloaded page resources', max=resources_count)
        for info in resources_info:
            _download_page_resource(info['url'], info['download_path'])
            progress_bar.next()
        progress_bar.finish()

    return page_file_path


def _download_page_resource(url, download_path):
    try:
        content = get_content(url)
        write_to_file(content, download_path)
    except (HTTPError, FileError):
        logger.warning(f"Page resource {url} wasn't downloaded")

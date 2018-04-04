# manga_downloader
Manga downloader with support for multiple sites, incremental downloads and searching

## supported sites
* mangahub.io
* mangakakalot.com
* manganelo.com
* dynasty-scans.com

## usage
* `manga.py search flower`
* `manga.py download https://mangahub.io/manga/transient-flower` 
* `manga.py download transient-flower` (downloads any additional chapters that have been released since initial download
* `manga.py list_chapters transient-flower` (lists available chapters)

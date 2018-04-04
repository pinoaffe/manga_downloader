#!/usr/bin/python
import requests
from bs4 import BeautifulSoup as bs
import os
import sys

download_dir="/home/user/manga" #CHANGEME


global mangasites
mangasites = {}


def bs_fetch(url):
    return bs(requests.get(url).text, "lxml")

def get_site(arg):
    global download_dir
    global mangasites
    if arg.startswith("http"):
        for key in mangasites:
            if mangasites[key].matches(arg):
                return [key] + mangasites[key].parse_url(arg)
    else:
        if not os.path.exists("%s/%s" %(download_dir, arg)):
            print("directory not yet downloaded, please specify full url")
        elif not os.path.exists("%s/%s/site_id" % arg):
            print("site_id not yet stored, please specify full url")
        else:
            with open("%s/%s/site_id" %(download_dir, arg)) as f:
                key = f.read()
                return [key.strip(), arg]


class manga_site(object):
    global download_dir
    def __init__(self, id, site_baseurl):
        self.id = id
        self.site_baseurl = site_baseurl

    def matches(self, url):
        if self.base_url in url:
            return True
        if self.base_url.replace("https", "http") in url:
            return True
        if self.base_url.replace("http", "https") in url:
            return True
        return False

    def search(self, search_string):
        pass

    def download_manga(self, manga_id):
        print(manga_id)
        if not os.path.exists("%s/%s" %(download_dir, manga_id)):
            os.makedirs("%s/%s" %(download_dir, manga_id))
        if not os.path.exists("%s/%s/site_id" %(download_dir, manga_id)):
            with open("%s/%s/site_id" %(download_dir, manga_id), "w") as f:
                f.write(self.id)
        for chapter_id in self.get_chapters(manga_id):
            self.download_chapter(manga_id, chapter_id)

    def download(self, parsed):
        if (len(parsed) == 3):
            self.download_page(*parsed)
        elif (len(parsed) == 2):
            self.download_chapter(*parsed)
        elif (len(parsed) == 1):
            self.download_manga(*parsed)

    def download_chapter(self, manga_id, chapter_id):
        if not os.path.exists("%s/%s/%s" % (download_dir, manga_id, chapter_id)):
            pages = self.get_pages(manga_id, chapter_id)
            os.makedirs("%s/%s/%s" % (download_dir, manga_id, chapter_id))
            print("\t", chapter_id)
            for page in pages:
                self.download_page(manga_id, chapter_id, page[0], page[1])

    def download_page(self, manga_id, chapter_id, page_id, page_url):
        filename = "%s.%s" %(page_id, page_url.split(".")[-1])
        if page_url.startswith("//"):
            page_url = "http:%s" % page_url
        if os.path.exists("%s/%s/%s/%s" % (download_dir, manga_id, chapter_id, filename)):
            print("\t\t", filename, "already download")
        else:
            print("\t\t", filename)
            with open("%s/%s/%s/%s" % (download_dir, manga_id, chapter_id, filename), "wb") as f:
                f.write(requests.get(page_url).content)

    def list_chapters(self, manga_id):
        for chapter in self.get_chapters(manga_id):
            print(chapter)

    def list_pages(self, manga_id, chapter_id):
        for page in self.get_pages(manga_id, chapter_id):
            print(page[0], page[1])

    def download_metadata(self, manga_id):
        pass

    def markread(self, manga_id):
        global download_dir
        print(manga_id, "marking as read")
        if not os.path.exists("%s/%s" %(download_dir, manga_id)):
            os.makedirs("%s/%s" %(download_dir, manga_id))
        if not os.path.exists("%s/%s/site_id" %(download_dir, manga_id)):
            with open("%s/%s/site_id" % (download_dir, manga_id), "w") as f:
                f.write(self.site_id)
        for chapter_id in self.get_chapters(manga_id):
            print("\t\t", chapter_id)
            path = "%s/%s/%s" % (download_dir, manga_id, chapter_id)
            if not os.path.exists(path):
                os.makedirs(path)


class mangakakalot(manga_site):
    def __init__(self, url):
        global mangasites
        self.base_url = "https://%s.com" % url
        self.id = url
        mangasites[self.id] = self

    def search(self, search_string):
        search_string = search_string.replace(" ", "_")
        soup = bs_fetch("%s/search/%s" %(self.base_url, search_string))
        mangas = soup.find_all("div", {"class": "daily-update-item"})
        for manga in mangas:
            if self.base_url in manga.a["href"] or self.base_url.replace("https", "http") in manga.a["href"]:
                print("\t%s" % manga.a["href"].split("/")[-1])

    def parse_url(self, url):
        if "%s/manga" % self.base_url in url:
            return [url.strip("/").split("/")[-1]]
        elif "%s/manga" % self.base_url.replace("https", "http") in url:
            return [url.strip("/").split("/")[-1]]
        elif "%s/chapters" & self.base_url in url:
            pass

    def get_chapters(self, manga_id):
        soup = bs_fetch("%s/manga/%s" %(self.base_url, manga_id))
        chapters = soup.find("div", {"class": "chapter-list"}).find_all("a")
        chapter_ids = [chapter["href"].split("/")[-1] for chapter in chapters]
        return (chapter_ids[::-1])

    def get_pages(self, manga_id, chapter_id):
        soup = bs_fetch("%s/chapter/%s/%s" % (self.base_url, manga_id, chapter_id))
        pages = soup.find("div", {"class": "vung-doc"}).find_all("img")
        to_return = []
        number = 1
        for page in pages:
            to_return += [[str(number).zfill(4), page["src"]]]
            number += 1
        return to_return

class mangahub(manga_site):
    def __init__(self):
        global mangasites
        self.base_url = "https://mangahub.io"
        self.id = "mangahub"
        mangasites[self.id] = self

    def parse_url(self, url):
        if "%s/manga" % self.base_url in url:
            return [url.strip("/").split("/")[-1]]
        elif "%s/chapter" % self.base_url in url:
            return [url.strip("/").split("/")[-2,-1]]

    def get_chapters(self, manga_id):
        soup = bs_fetch("%s/manga/%s" % (self.base_url, manga_id))
        chapters = soup.find_all("li", {"class": "list-group-item"})
        chapter_ids = [chapter.a["href"].strip("/").split("/")[-1] for chapter in chapters]
        return (chapter_ids[:-1])

    def get_pages(self, manga_id, chapter_id):
        soup = bs_fetch("%s/chapter/%s/%s" % (self.base_url, manga_id, chapter_id))
        count = int(soup.find("div", {"class": "container-fluid"}).p.text.split("/")[-1])
        to_return = []
        for page_id in range(1,count+1):
            url = "https://cdn.mangahub.io/file/imghub/%s/%s/%s.jpg" %(manga_id, chapter_id.split("-")[-1], page_id)
            to_return += [[str(page_id).zfill(4),url]]
        return to_return

    def search(self, keyword):
        soup = bs_fetch("%s/search?q=%s" % (self.base_url, keyword.replace(" ", "%20")))
        items = soup.find("div", {"id": "mangalist"}).find_all("div", {"class": "media-manga"})
        for item in items:
            print("\t" + item.a["href"].strip("/").split("/")[-1])

class dynasty_scans(manga_site):
    def __init__(self):
        global mangasites
        self.base_url = "https://dynasty-scans.com"
        self.id = "dynasty-scans"
        mangasites[self.id] = self

    def parse_url(self, url):
        if "%s/series" % self.base_url in url:
            return [url.strip("/").split("/")[-1]]
        elif "%s/chapters" % self.base_url in url:
            pass

    def get_chapters(self, manga_id):
        soup = bs_fetch("%s/series/%s" % (self.base_url, manga_id))
        chapters = soup.find("dl", {"class": "chapter-list"}).find_all("dd")
        chapter_ids = [chapter.a["href"].strip("/").split("/")[-1] for chapter in chapters]
        return (chapter_ids)

    def search(self, keyword):
        pass

    def get_pages(self, manga_id, chapter_id):
        soup = bs_fetch("%s/chapters/%s" % (self.base_url, chapter_id))
        script = soup.body.script.string
        script = script[script.find("[{")+1:script.find("}];")+1]
        pages = script.split("},{")
        to_return = []
        for page in pages:
            page = page.strip("{}").split(",")
            page_url = "%s/%s" %(self.base_url[:-1], page[0].split("\"")[-2])
            page_id = page[1].split("\"")[-2]
            to_return += [[page_id, page_url]]
        return to_return


mangakakalot("mangakakalot")
mangakakalot("manganelo")
dynasty_scans()
mangahub()



if len(sys.argv) < 3:
    print("not enough arguments")
else:
    if sys.argv[1] == "download":
        parsed = get_site(sys.argv[2])
        mangasites[parsed[0]].download(parsed[1:])
    elif sys.argv[1] == "search":
        for key in mangasites:
            print(key)
            mangasites[key].search(" ".join(sys.argv[2:]))
    elif sys.argv[1] == "list_chapters":
        parsed = get_site(sys.argv[2])
        mangasites[parsed[0]].list_chapters(*parsed[1:])
    elif sys.argv[2] == "markread":
        parsed = get_site(sys.argv[2])
        mangasites[parsed[0]].markread(*parsed[1:])

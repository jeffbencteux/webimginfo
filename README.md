# webimginfo

## Description

Reconnaissance tool to gather images metadata from websites.

Images contains numerous metadata fields depending on their filetype (JPG, PNG...). These fields include interesting information for reconnaissance purposes such as: names, telephone numbers, email addresses or URLs. Often, website editors do not strip the images hosted on their websites from these information, making leaks possible. This tool allow you to retreive images hosted on a website and parse them to obtain potentially interesting information.

## Dependencies

Rely on:

* BeautifulSoup
* PyExiftool

```
pip3 install -r requirements.txt
```

## Features

Agnostic to image filetypes, e.g. you may end up collecting a lot of SVG without metadata but the tool works without knowing a file is a PNG or JPG.

Currently supports HTML `<img>` attributes:

* src
* srcset (partially)
* data-src
* data-srcset (partially)
* data-lazy

supports `data:` scheme in these attributes with:

* base64 encoded content

For now, all collected images are stored in a local folder named "extracted_images". This can grow pretty quickly, be sure to have enough storage.

## Examples

```bash
$ ./webimginfo.py -h
usage: webimginfo.py [-h] [-o OUT] url

positional arguments:
  url                URL to get images from

options:
  -h, --help         show this help message and exit
  -o OUT, --out OUT  Output filename
```

Le Monde:

```bash
$ ./webimginfo.py https://www.lemonde.fr -o lemonde
WebImgInfo v1.0
Scraping https://www.lemonde.fr


Analyzing new image tag
src: https://img.lemde.fr/2023/04/06/0/0/4020/2680/180/0/95/0/e643f1f_1680785011106-000-33c29en.jpg
alt: Réseau électrique aux alentours de Verfeil (Haute-Garonne), le 25 mars 2023.
Writing to disk as ./extracted_images/https__img.lemde.fr_2023_04_06_0_0_4020_2680_180_0_95_0_e643f1f_1680785011106-000-33c29en.jpg

Analyzing new image tag
[...]

Analyzing ./extracted_images/https__img.lemde.fr_2023_04_06_[...].jpg

[names]
IPTC:Source: AFP
IPTC:CopyrightNotice: AFP or licensors
IPTC:Credit: AFP
IPTC:Credit: AFP
IPTC:By-line: CHARLY XXXXXXXXXXX

[addresses]
IPTC:City: Verfeil
IPTC:Province-State: Haute-Garonne
IPTC:Country-PrimaryLocationName: France
IPTC:Country-PrimaryLocationCode: FRA

[emails]

[phone]

[urls]

[dates]
File:FileModifyDate: 2023:04:07 11:59:01+02:00
File:FileAccessDate: 2023:04:07 11:58:21+02:00
File:FileInodeChangeDate: 2023:04:07 11:59:01+02:00
ICC_Profile:ProfileDateTime: 1998:02:09 06:49:00
IPTC:DateSent: 2023:03:25
IPTC:TimeSent: 19:10:27+00:00
IPTC:DateCreated: 2023:03:25
IPTC:TimeCreated: 19:11:40+01:00

[platform]

[software]
IPTC:OriginatingProgram: g2mapping/libg2 3.9.39

[misc/context]
IPTC:ObjectName: FRANCE-ENERGY-ELECTRICITY
IPTC:Keywords: ['energy', 'Horizontal', 'ILLUSTRATION', 'ENERGY AND RAW MATERIALS', 'ELECTRICITY', 'ELECTRICITY PYLON', 'SUNRISE AND SUNSET']
IPTC:Caption-Abstract: This photograph taken on March 25, 2023, shows an electricity pylon with a sunset in the background near Verfeil, southwestern France. (Photo by Charly XXXXXXX / AFP)
IPTC:SubjectReference: IPTC:04005000:economy, business and finance:energy and resource:
IPTC:SupplementalCategories: energy and resource
```

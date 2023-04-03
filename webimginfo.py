#!/usr/bin/python
#
# Copyright (c) 2023, Jeffrey Bencteux
# All rights reserved.

# This source code is licensed under the GPLv3 license found in the
# LICENSE file in the root directory of this source tree.

import os
import argparse
import urllib.parse
import requests
import string
from bs4 import BeautifulSoup
import exiftool
import base64

log_enabled=False
outfile=None

def base_url(url, with_path=False):
	parsed = urllib.parse.urlparse(url)
	path   = '/'.join(parsed.path.split('/')[:-1]) if with_path else ''
	parsed = parsed._replace(path=path)
	parsed = parsed._replace(params='')
	parsed = parsed._replace(query='')
	parsed = parsed._replace(fragment='')
	return parsed.geturl()

def full_url(args, src):
	full_url = ""
	if "http" not in src:
		full_url = base_url(args.url) + src
	else:
		full_url = src
	return full_url

def log(s, end="\n"):
	print(s, end=end)

	if log_enabled:
		outfile.write(s)
		outfile.write(end)

def print_ok(s, end="\n"):
	log("\033[92m" + s + "\033[0m", end=end)

def print_ko(s, end="\n"):
	log("\033[91m" + s + "\033[0m", end=end)

def print_warning(s, end="\n"):
	log("\033[93m" + s + "\033[0m", end=end)

def print_info(s, end="\n"):
	log("\033[94m" + s + "\033[0m", end=end)

def normalize_name(name):
	res = ""
	for c in name:
		if c in string.ascii_letters or c in string.digits or c == "-" or c == "_" or c == ".":
			res = res + c
	return res

def get_last_n_chars(s, n):
	if len(s) < n:
		return s
	else:
		return s[:n]

def write_image_to_disk(path, content):
	log("Writing to disk as " + path)
	f = open(path, "wb")
	f.write(content)
	f.close()


def parse_data_scheme(src):
	# Only supporting b64 images for now
	if not src.startswith("data:"):
		return None

	splitted = src.split(",")

	if len(splitted) < 2:
		print_ko("Could not parse data: scheme")
		print_ko(src)
		return None

	if splitted[0][-6:] == "base64":
		b64_content = splitted[1].strip()

		try:
			content = base64.b64decode(b64_content)
		except:
			print_ko("Could not decode base64")
			print_ko(src)
			return None

		return content
	return None

def analyze_image_tag(args, img):
	url = args.url

	log("\nAnalyzing new image tag")
	# Just taking the first in the set in these cases. Not really exhaustive.
	if img.has_attr("data-srcset"):
		first_url = img["data-srcset"].split(' ')[0]
		img_url = first_url
	elif img.has_attr("srcset"):
		first_url = img["srcset"].split(' ')[0]
		img_url = first_url
	# data-src has priority over src as I have seen websites where src is used
	# with useless values over data-src
	elif img.has_attr("data-src"):
		img_url = img["data-src"]
	elif img.has_attr("data-lazy"):
		img_url = img["data-lazy"]
	elif img.has_attr("src"):
		img_url = img["src"]
	else:
		print_ko("No src/srcset/data-src/data-srcset/data-lazy attribute")
		return None, None

	if img_url.startswith("data:"):
		img_content = parse_data_scheme(img_url)
	else:
		img_url = full_url(args, img_url)

		try:
			img_req = requests.get(img_url)
		except:
			print_ko("Could not request image URL " + img_url)
			return None, None

		if img_req.status_code != 200:
			print_ko("Could not extract image with source " + img_url)
			return None, None

		log("src: " + img_url)
		img_content = img_req.content

	if img.has_attr("alt"):
		log("alt: " + img["alt"])

	return img_url, img_content

def print_field_if_exists(d, field):
	if field in d:
		log("{}: {}".format(field, d[field]))

def print_fields(theme, d, fields):
	log("\n[", end='')
	print_info(theme, end='')
	log("]")
	for field in fields:
		print_field_if_exists(d, field)

def exiftool_analysis(filenames):
	if len(filenames) == 0:
		return

	et = exiftool.ExifToolHelper()

	try:
		metadata = et.get_metadata(filenames)
	except:
		log(filenames)
		print_ko("Could not parse images with exiftool")
		return

	for d in metadata:
		log("\nAnalyzing ", end='')
		print_ok(d["SourceFile"])

		#for i in d:
		#	print("{}: {}".format(i, d[i]))

		# Names
		names = ["XMP:Author", "XMP:Creator", "EXIF:Artist", "XMP:Source", "IPTC:Source", "EXIF:Copyright", "IPTC:CopyrightNotice", "IPTC:Credit",  "XMP:Credit", "IPTC:Credit", "IPTC:Writer-Editor", "IPTC:By-line"]
		print_fields("names", d, names)

		# Addresses
		addresses = ["XMP:CreatorAddress", "XMP:CreatorCity", "XMP:CreatorCountry", "XMP:CreatorPostalCode", "XMP:CreatorRegion", "IPTC:City", "IPTC:Province-State", "IPTC:Country-PrimaryLocationName", "IPTC:Country-PrimaryLocationCode", "IPTC:Sub-location"]
		print_fields("addresses", d, addresses)

		# Email
		email = ["XMP:CreatorWorkEmail"]
		print_fields("emails", d, email)

		# Telephone
		telephone = ["XMP:CreatorWorkTelephone"]
		print_fields("phone", d, telephone)

		# URLs
		urls = ["XMP:CreatorWorkURL", "XMP:LicensorURL:", "XMP:WebStatement"]
		print_fields("urls", d, urls)

		dates = ["File:FileModifyDate", "File:FileAccessDate", "File:FileInodeChangeDate", "ICC_Profile:ProfileDateTime", "PNG:Datecreate", "PNG:Datemodify", "PNG:ModifyDate", "XMP:MetadataDate", "XMP:ModifyDate", "XMP:CreateDate", "IPTC:DateSent", "IPTC:TimeSent", "IPTC:DateCreated", "IPTC:TimeCreated"]
		print_fields("dates", d, dates)

		# Platform
		platform = ["XMP:HistorySoftwareAgent", "XMP:Platform"]
		print_fields("platform", d, platform)

		# Software
		software = ["EXIF:Software", "XMP:CreatorTool", "XMP:HistorySoftwareAgent", "IPTC:OriginatingProgram"]
		print_fields("software", d, software)

		# Misc
		context = ["EXIF:ImageDescription", "XMP:Description", "EXIF:UserComment", "IPTC:ObjectName", "IPTC:Keywords", "IPTC:Headline", "IPTC:Caption-Abstract", "IPTC:SubjectReference", "IPTC:SupplementalCategories", "IPTC:SpecialInstructions"]
		print_fields("misc/context", d, context)

def analyze_images_from_html(args, extract_path, html):
	if not os.path.exists(extract_path):
		os.mkdir(extract_path)

	soup = BeautifulSoup(html, "html.parser")
	img_tags = soup.find_all('img')
	img_filenames = []

	for img in img_tags:
		img_url, img_content = analyze_image_tag(args, img)

		if img_content is None:
			print_ko("No content for image")
			continue

		img_extract_path = extract_path + "/" + normalize_name(get_last_n_chars(img_url.replace("/", "_").replace("\n", ""), 200 - len(extract_path)))
		write_image_to_disk(img_extract_path, img_content)
		img_filenames.append(img_extract_path)

	exiftool_analysis(img_filenames)

def parse_page(args):
	resp = requests.get(args.url)
	page_html = resp.text

	analyze_images_from_html(args, "./extracted_images", page_html)

def main():
	global outfile
	global log_enabled

	parser = argparse.ArgumentParser()
	parser.add_argument("url", help="URL to get images from", type=str)
	#parser.add_argument("-e", "--extract", help="Keep extracted images on disk", action="store_true")
	parser.add_argument("-o", "--out", help="Output filename", type=str)

	args = parser.parse_args()

	if (args.out):
		log_enabled = True
		outfile = open(args.out, "w")

	log("WebImgInfo v1.0")
	log("Scraping ", end='')
	print_ok(args.url)
	log("")

	parse_page(args)

	if (args.out):
		outfile.close()
main()


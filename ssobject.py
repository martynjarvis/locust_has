import requests
import urlparse
import time
from locust import events
import xml.etree.ElementTree as ET

import hlslocust.asobject as asobject
import hlslocust.cast as cast
import hlslocust.hlserror as hlserror

class Manifest(asobject.ASManifest):
    def __init__(self,name,url):
        self.name = name
        self.url = url
        self.bitrates = []
        self.times = []
        self.tree = None

    def parse(self, manifest):
        self.tree = ET.fromstring(manifest)


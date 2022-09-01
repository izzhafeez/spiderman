from __future__ import annotations
from functools import cached_property
import re

class Href():
  href: str
  domain: str
  url: str
  open_tag: str
  close_tag: str
  
  OPEN_TAG = "(href"
  CLOSE_TAG = "href)"
  
  def __init__(self, href: str, domain: str, url: str):
    self.href = href
    self.domain = domain
    self.url = url
    
    self.open_tag = Href.OPEN_TAG
    self.close_tag = Href.CLOSE_TAG
  
  def __str__(self) -> str:
    return self.clean_href
  
  def __repr__(self) -> str:
    return self.clean_href
  
  @cached_property
  def clean_href(self) -> str:
    if self.href[0] == "#":
      href = re.split("#[^#]*$", self.url)[0] + self.href
      return href
    elif self.href[0:2] == "//":
      href = "http:" + self.href
      return href
    elif self.href[0] == "/":
      href = "http://" + self.domain + self.href
      return href
    return self.url
  
  @cached_property
  def enclosed_href(self) -> str:
    return self.open_tag + str(self) + self.close_tag
  
class SelfHref(Href):
  pass

class IntHref(Href):
  pass

class ExtHref(Href):
  pass
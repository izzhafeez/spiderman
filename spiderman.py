from typing import List, Pattern, Union

from bs4 import BeautifulSoup
from urllib.parse import urlparse
import copy
import pandas as pd
import re
import requests

from hrefs.href import Href

class Spiderman():
  """
  A class to represent data retrieved from a website.
  Functions can also be applied to extract more information.
  
  Attributes:
    url [str]: the link itself
    domain [str]: the domain link
    html [BeautifulSoup object]: the contents of the page, in html format
    hrefs [list of str]: all the outward links of the page
  """
  
  url: str
  domain: str
  html: BeautifulSoup
  hrefs: List[Href]
  
  def __init__(self, url: str):
    """
    Initialise Spiderman object.

    Args:
      url (str): the link to the site
    """
    
    self.url = url
    self.domain = urlparse(url).netloc
    self.html = BeautifulSoup(requests.get(url).text,'html.parser')
    self.hrefs = [
      Href(a['href'], self.domain, self.url) for a in self.html(href=True)
    ]
    
  def __str__(self):
    """
    When the object itself is called, return a dictionary containing its url and hrefs.
    """
    
    return {"url": self.url,
            "hrefs": self.hrefs}
    
  def attach_hrefs(self, subset: Union[List[str], str, Pattern]="", edit: bool=False):
    """
    This function aims to take each "a"-tagged element and extract its url and the text it contains.
    After that, the url is appended to the text, and the whole thing is returned as a string back to the BeautifulSoup object.
    In order to keep track of what changes I've made to the BeautifulSoup object, as well as to more easily find the urls, a "container" is placed around the urls.
    That's where Href.OPEN_TAG and Href.CLOSE_TAG come into play.
    They basically surround the url and makes the url easier to find using search terms.
    By default, they convert an "a" tag from <a href="url.com">text</a> into text(hrefurl.comhref).
    But of course, they can be changed.

    Args:
      subset [list of html tags like 'p', 'h3']: controls which tags to conduct this operation on (eg. only want to change the "a" tags within div elements)
      edit [boolean]: controls whether to change the self.html attribute (setting it to False will output the result to self.editHtml attribute instead)
    """
    
    if edit:
      html = self.html
    else:
      self.edit_html = copy.copy(self.html)
      html = self.edit_html
      
    for tag in html(subset):
      for a in tag("a", href=True):
        if hasattr(a, "string"):
          a.string = a.string + repr(Href(a["href"], self.domain, self.url))
        else:
          a.string = repr(Href(a["href"], self.domain, self.url))
          
  def get_tables(self,
                 merge=True,
                 href=True,
                 href_separate=True,
                 edit=True) -> None:
    """
    The simple function is to retrieve all the tables within the html.
    That simple task is done using Pandas' read_html() function.
    However, combining it with the previously discussed function yields more useful results.
    You see, as it stands, quite alot of tables contain links within their cells and as such, the pd.read_html() function doesn't work as well.
    So, this function rips the links out of their "a" tags and places them either into separate columns, or attached to the text.
    Under the former, for each row, all the links found are gathered into a single column.


    Another purpose of this function is to combine tables with identical column headers.
    Under the condition merge = True, the code looks for groups of tables with the exact same set of column headers.
    From that, it returns the merged tables.

    Args:
      merge [boolean]: refer to above
      href [boolean]: whether to include the links, or too discard them altogether
      hrefSeparate [boolean]: whether to separate the hrefs into a separate column
      edit [boolean]: there are two different places where html content is stored (self.html and self.editHtml). As such, this parameter will choose which one to use.
    """
    
    if href:
      self.attach_hrefs(subset = ['td'], edit = False)
    
    if edit:
      self.tables = pd.read_html(
        re.sub('[\n\t]+',
               'Ǟ',
               str(self.html('table'))
               )
        )
    else:
      self.tables = pd.read_html(
        re.sub('[\n\t]+',
               'Ǟ',
               str(self.edit_html('table'))
               )
        )
    
    self.tables = [table.fillna('') for table in self.tables]
      
    if href_separate:
      
      for table in self.tables:
        
        table['Links'] = table.apply(
          lambda x: '\n'.join(
            re.findall(
              re.compile(Href.OPEN_TAG + "(.*?)" + Href.CLOSE_TAG),
              ''.join(list(x))
              )
            ), axis=1)
        
        table.loc[:,table.columns != 'Links'] = table.loc[:,table.columns != 'Links']\
          .applymap(
            lambda x: re.sub(
              re.compile(Href.OPEN_TAG + ".*?" + Href.CLOSE_TAG),'',x
              )
            )

    self.merged_tables = []
    self.unique_tables = []

    if merge:
      
      column_sets = {}
      for table in self.tables:
        try:
          columns = '||'.join(sorted(list(table.columns)))
          if columns not in column_sets:
            column_sets[columns] = [table]
          else:
            column_sets[columns].append(table)
        except:
          self.unique_tables.append(table)
      
      for column_set in column_sets:
        self.merged_tables.append(pd.concat(column_sets[column_set]))
    
  def get_lists(self, href: bool=True, edit: bool=False) -> None:
    """
    Simliar to the getTables() function, the getLists() function consolidates the urls found within list elements.

    Args:
      href [boolean]: whether to include the links, or too discard them altogether
      edit [boolean]: there are two different places where html content is stored (self.html and self.editHtml). As such, this parameter will choose which one to use.
    """
     
    if href:
      self.attach_hrefs(subset = re.compile('[oi]l'))
      
    if edit:
      self.raw_lists = self.html(re.compile('[oi]l'))
    else:
      self.raw_lists = self.edit_html(re.compile('[oi]l'))
      
    self.lists = []
    
    for raw_list in self.raw_lists:
      ss = pd.DataFrame(
        [li.get_text() for li in raw_list('li')],
        columns = ['Text']
        )
      ss['Hrefs'] = ss['Text']\
        .apply(
          lambda x: '\n'.join(
            re.findall(
              re.compile(Href.OPEN_TAG + "(.*?)" + Href.CLOSE_TAG), x
              )
            )
          )
      ss['Text'] = ss['Text']\
        .apply(
          lambda x: re.sub(
            re.compile(Href.OPEN_TAG + ".*?" + Href.CLOSE_TAG), '', x
            )
          )
      self.lists.append(ss)
      
  def cleanHrefs(self) -> None:
    """
    This applies the cleanHref() function to all the links in the website.
    """
    
    self.all_hrefs = []
    self.self_hrefs = []
    self.int_hrefs = []
    self.ext_hrefs = []
    
    for href in self.hrefs:
      try:
        if href.href[0] == '#':
          self.self_hrefs.append(re.split('#[^#]*$', self.url)[0] + href.href)
        elif href.href[0:2] == '//':
          self.ext_hrefs.append('http:' + href.href)
        elif href.href[0] == '/':
          self.int_hrefs.append('http://' + self.domain + href.href)
        else:
          self.ext_hrefs.append(href)
        self.all_hrefs.append(href)
      except: pass
    
    self.all_hrefs = list(set(self.all_hrefs))
    self.self_hrefs = list(set(self.self_hrefs))
    self.int_hrefs = list(set(self.int_hrefs))
    self.ext_hrefs = list(set(self.ext_hrefs))
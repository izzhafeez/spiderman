from typing import List, Union

import bs4

def find_previouses(soup: bs4.Tag, tag: str, n: int) -> Union[bs4.Tag, bs4.NavigableString, None]:
  
  """
  The find_previous() function in BeautifulSoup searches for previous occurrence of a particular tag.
  However, there often are cases where we need to use this function several times, having nested functions like (find_previous(find_previous(soup))).
  Before I found out about the find_all_previous() function, I needed a shorthand for searching for tags.
  So here I am

  Args:
    soup [BeautifulSoup object]: the soup object that you want to search in
    tag [HTML tag like 'p' or 'h3', or a list of them]: the tags that you want to search for
    n [int]: the number of times the function find_previous() is to be repeated
  """

  new_soup = soup
  for _ in range(n):
    if new_soup == None:
      break
    new_soup = new_soup.find_previous(tag)
  return new_soup


def find_nexts(soup: bs4.Tag, tag: str, n: int) -> Union[bs4.Tag, bs4.NavigableString, None]:

  """
  The find_next() function in BeautifulSoup searches for next occurrence of a particular tag.
  However, there often are cases where we need to use this function several times, having nested functions like (find_next(find_next(soup))).
  Before I found out about the find_all_next() function, I needed a shorthand for searching for tags.
  So here I am

  Args:
    soup [BeautifulSoup object]: the soup object that you want to search in
    tag [HTML tag like 'p' or 'h3', or a list of them]: the tags that you want to search for
    n [int]: the number of times the function find_next() is to be repeated
  """

  new_soup = soup
  for _ in range(n):
    if new_soup == None:
      break
    new_soup = new_soup.find_next(tag)
  return new_soup


def all_str(soup: bs4.Tag, joiner: str="") -> str:

  """
  The stripped_strings attribute takes a BeautifulSoup object and removes the whitespace elements.
  However, it outputs in an iterable format.
  As such, allstr() is shorthand for the cleanup process.

  Args:
    soup [BeautifulSoup object]: the soup object that you want to clean
    joiner [str]: how you want to join the list
  """

  return joiner.join(list(soup.stripped_strings))


def soupstr(soup: bs4.Tag) -> List[str]:

  """
  Similar to the above, soupstr() just converts into a list instead of joining all the strings together.

  Args:
  soup [BeautifulSoup object]: the soup object that you want to clean
  """

  return list(soup.stripped_strings)
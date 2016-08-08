import urllib2
from pyatom import AtomFeed
import dateutil.parser
import re
import mod_python
import BeautifulSoup

def get_favicon(soup, baseurl):
   icon_link = soup.find("link", rel="shortcut icon")
   if not icon_link:
      icon_link = baseurl + "/favicon.ico"
   #icon = urllib.urlopen(icon_link['href'])  #FIXME: maybe check for existence and favicon meta tag   
   return icon_link

def get_forumtitle(soup):
   forumtitle = soup.find("title")
   match = re.match("^(.*) &bull; View forum - (.*)$", forumtitle.contents[0])
   if match:
      forumtitle = match.group(1) + " - " + match.group(2)
   else:
      forumtitle = "(Forum title not found)"
   return forumtitle

def get_baseurl(forumurl):
   urlmatch = re.match('https?://[^/]+', forumurl, re.I)
   if urlmatch:
      baseurl = urlmatch.group()
   else:
      req.status = mod_python.apache.HTTP_INTERNAL_SERVER_ERROR
      raise Exception("Failed to extract base url from "+forumurl)
   return baseurl

def get_soup(forumurl):
   try:
      response = urllib2.urlopen(forumurl)
      page = response.read()
   except urllib2.HTTPError, error:
      req.status = mod_python.apache.HTTP_INTERNAL_SERVER_ERROR
      gerror = "Error returned by forum: " + error.read();
      raise Exception("Failed to fetch forum source code. Is the forum at "+forumurl+" down? " + gerror)

   soup = BeautifulSoup.BeautifulSoup(page)
   return soup

def index(req):
   forumurl = "writeme" # replace with e.g. "https://forums.factorio.com/viewforum.php?f=3"
   if forumurl == "writeme":
      req.status = mod_python.apache.HTTP_INTERNAL_SERVER_ERROR
      return "The admin for this script needs to manually set the 'forumurl' parameter in the source code"

   baseurl = get_baseurl(forumurl);
   soup = get_soup(forumurl)

   forumtitle = get_forumtitle(soup)

   #generate feed
   feed = AtomFeed(title=forumtitle,
                   url=forumurl,
                   icon=get_favicon(soup, baseurl))
   #Add forum topics
   for a in soup.findAll("a", { "class" : "topictitle" }):
      datestring = a.parent.contents[-1]
      datematch = re.match('^ &raquo; (.*?)\s*$', datestring, re.M)
      datestring_trimmed = datematch.group(1)
      published = updated = dateutil.parser.parse(datestring_trimmed)

      author_a = a.parent.find("a", { "class" : "username-coloured"})
      if author_a:
         author = author_a.string
      else:
         author = "(author not found)"

      #phpBB generates a unique new session id (sid) for each forum
      #download, and adds this to all urls. This will make feed
      #readers interpret each link as unique each time it polls. So we
      #need to remove the sid=...
      url = baseurl + "/" + a["href"]
      url = re.sub('&sid=[0-9a-f]+','', url)

      feed.add(title=a.string,
               url=url,
               published=published,
               updated=updated,
               author=author,
               )

   return feed.to_string()

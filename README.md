A python script to generate an atom feed from a phpBB subforum, for use in a web feed reader.

For whatever reason, phpBB has buildin feeds for all new topic posts
in all forums, and all posts (including in existant topics) in one
subforum. But not a feed for only new topics in one subforum. This
script created such a feed froma forum url.

Usage: 

1. Put the script somewhere under your webserver root
2. Enable python scripting in your webserver configuration
3. Install the python packages mod_python, BeautifulSoup, and pyatom
4. Edit the "forumurl" variable in the script (grep for "writeme"), replacing it with a link to a phpBB subforum, e.g. "https://forums.factorio.com/viewforum.php?f=3"
5. Now the feed is available as www.example.com/phpbb_forum_topics_as_atom.py

The script works by hackily parsing phpBB html, so it is possible that it will break
or fail to work with some versions of phpBB
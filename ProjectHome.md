## What is it? ##

**Pr0nbot** is a spidering bot that takes a single URL and wanders the web downloading images and videos from free porn sites. The project started as a joke that went too far, then became a fun way to improve my Python skills. Right now it's a fairly robust spidering engine which can parse some pretty broken HTML without crashing (and boy, porn sites have horrible, horrible code).

Major features are:

  * Redirection resolution: Pr0nbot knows how to deal with the most common URL redirection tactics, avoiding neverending interlinking galleries (a.k.a. circle-jerking).

  * Save state: when interrupted, the spidering can be resumed at any time.

  * User-customizable ignore list, to avoid unwanted links and fine-tune the porn to the user's taste. ;-)

  * Comprehensive run-time options.


## Installation: ##

  * **Linux:** Use the install script provided or simply copy pr0nbot.py to somewhere on your executable path, rename it to 'pr0nbot' sans '.py' and make it executable. That's exactly what the install script does, by the way.

  * **Windows:** Put the script file anywhere you like and run it from the command window (python pr0nbot.py ...).

Pr0nbot requires [Python](http://www.python.org) 2.4 or higher (I think!).


## Usage: ##

**pr0nbot _options_ url**

|url|Starting URL for spidering.|
|:--|:--------------------------|
|-d x, --dir=x|Directory for downloaded pr0n (default: pr0n).|
|-m x, --min=x|Minimum size in k for download (default 25).|
|-a, --aggro|AGGRO MODE! Downloads from <img> tags too.<br>
<tr><td>-i, --ignore</td><td>Ignores the saved spidering state.</td></tr>
<tr><td>-v, --verbose</td><td>Be talkative and annoying. </td></tr>
<tr><td>-q, --quiet</td><td>Be absolutely quiet.       </td></tr>
<tr><td>-h, --help</td><td>This help screen (whee!).  </td></tr>
<tr><td>--nomovies</td><td>Don't download movies.     </td></tr>
<tr><td>--nopics</td><td>Don't download pictures.   </td></tr></tbody></table>


<h2>Usage tips: ##

  * When first run, a configuration file (.pr0nbot.rc) is created in the home directory ($HOME on linux, %USERPROFILE% on windows) containing the ignore list. This list can be freely modified by the user. See the comments inside the file itself for more information.

  * The spidering state is saved to a pr0nbot.state file inside the current pr0n directory each time Pr0nbot is interrupted. From then on, you just have to provide the directory name and all the spidering parameters are read from the state file (except for verbose/quiet settings).

  * The default dir used for downloaded porn is 'pr0n', created on the current directory. If it exists with a saved state within, Pr0nbot can be run without any command line parameters to resume the spidering.

  * The best URLs to start the spidering are gallery pages and link lists. Some favourites: http://www.thehun.com, http://www.heinzhard.com, http://galeradopol.blogspot.com (works better with --aggro -m 40)... you get the idea.


## Bugs: ##

  * Pr0nbot has been found to work on Linux and Windows without problems, but fails to start on MacOS X. Since I don't have a mac, I really don't know what the problem is.

  * The spidering can be safely interrupted with Ctrl+C, but sending a SIGKILL terminates the Python interpreter without giving Pr0nbot a chance to save the spidering state. I couldn't find a way to trap signals in Python, so this is how it is (for now).


(c) 2007 by Fabio FZero (GPL v2)
# API Skeleton

## About
The API Skeleton is designed to be a starting point for any API which requires users, authentication
and authorisation, in other words, quite a lot of APIs. The intention is to create a robust, simple,
tested and documented way to start building a CRUD API.

The available endpoints, decorators, classes etc. are generic enough to be used in your own API and
then expanded into your use case. A design consideration was to write as little boilerplate code as
possible. This is done by using  open-source components whenever possible instead of writing bespoke
code to solve common problems. The benefit is less code and (hopefully) quality documentation. The
downside is that when it doesn't do quite what you want, not so nice workarounds have to be built.
As with anything in programming (and life), there are tradeoffs to be made and this was the
experiment I chose to follow. It definitely wasn't down to being work-shy. I swear.

## Requires
```
python 3.8+
```

## Flask
Flask is the main game in town with the API Skeleton. As the de-facto Python API library, it is
well-supported, documented, extended and deployed in production. This made it the obvious choice
when considering my experiment of writing as little code as possible (or maybe I'm just lazy).

To start the Flask app take a look at the [Manager section](#manager) below, as an alternative to
loading [environment variables](#environment-variables) and running things directly from the command
line.

## Flask extensions
As you can see from the [requirements](requirements.txt) file, there are a LOT of Flask extensions.
These do the heavy lifting so that I don't have to. I'm putting the open source community to work
for me, so I can lay about on the beach while I code these measly few lines. I won't discuss every
one of these as I suspect most of them are straightforward and obvious as to why they were used.
They are also commonly used in other Flask projects (one might say I stole their decisions).

### Flask-RESTX
[Flask-RESTX](https://flask-restx.readthedocs.io) is the extension with probably the largest impact
on the project. It is a fork of the earlier Flask-RESTPlus project (which sadly the maintainer seems
to have gotten burned out by over the years). It uses Python decorators on Flask endpoints for a
number of purposes. First, it automatically generates [Swagger/Open API](https://swagger.io) files.
As someone who has written thousands of lines of this endless JSON soup, this is what caught my
attention. Second, using decorators it also does data validation and serialisation/de-serialisation.
Again as someone who has written a decent chunk of Python to do this, I was immediately drawn to the
library when it was introduced to a work project I was involved with. Writing less repetitive code
is always a good thing in my book.

It is of course, not a silver bullet. The library generally did what I expect but there were also
some very frustrating debugging sessions (how good is open source for debugging) while reading the
documentation. These would have happened far less with ~~terrible~~ awesome code I had written
myself. But the library has years of other developers great knowledge and time embodied in it, so I
decided the trade-off was worth it. It is an age-old question. And by age-old, I mean probably 20
years since open source let us do this.

### Flask-Babel
Even though I only speak three languages (English, Strayan and Python), I thought it would be
interesting to add the ability to do programmatic internationalisation (i18n). I found the industry
standard [Babel](https://babel.pocoo.org) to be most enjoyable to use, and it has a nice [Flask
extension](https://flask-babel.tkte.ch).

Every string that a user will ever see has been removed from the main execution code and placed into
a [single base file](app/i18n/base.py) which is written in Australian English (such as it is) which
can then be translated into specific Babel files by speakers of other tongues such as New Zealand
English or Irish English or English English. 

### Flask-SQLAlchemy
This is a nice little extension which simplifies the use of
[SQLAlchemy](https://www.sqlalchemy.org) in a Flask app. I debated about using SQLAlchemy. The whole
ORM vs raw SQL debate. My initial thoughts were, man it's great that I can just get the ORM to do
all the hard SQL work for me. Then I did some reading and talking to other developers and discovered
it's not so clear-cut. ORMs can be much slower because they don't allow the SQL engine, or the
developer for that matter, to do much optimisation. I also ended up doing a lot of raw SQL in Python
at work where I was learning from a grandmaster, and found that I actually quite enjoy it. I do love
writing a good clean SQL query nowadays. At that point though I was quite committed (pun intended?)
to ORM for this project. Plus I really love the migration tools when combined with
[Alembic](#alembic). For my next project (which I intend to productionise) I think I may use
SQLAlchemy because I do love writing and interacting with the models in Python, but I will have that
raw SQL ability in my tool-belt which I can deploy into SQLAlchemy when necessary.

## Database
### SQLite
For the development environment I went with a file based [SQLite](https://www.sqlite.org/) database.
I know that it is pretty basic, but I had never really used it before, so I thought it was worth a
crack for a non-work related project. I can report that it is fine to use, but you can't beat a good
Docker database for local development.

For in-memory testing as recommended in the [Testing section](#testing) below I went with SQLite
in-memory. It is fast and simple to set up, and I had no issues with it.

### Docker
For the real deal, I went with a [Docker](https://www.docker.com) database. As discussed in the
[Testing section](#testing), this Docker database was used to represent a "deployed" database.
Starting and stopping the database is handled by a management script which is discussed in the
[Manager section](#manager) below.

For a real project, and now that I've tried SQLite, I would just continue my love affair with
Docker.

### Alembic
[Alembic](https://alembic.sqlalchemy.org/en/latest) is a library which works with SQLAlchemy to do
database migrations. You run a few commands, and it generates the migration scripts into this
[directory](migrations/versions). It can be run as detailed in the [Manager section](#manager) below.

## Security
Decorators are used on the Flask endpoints when necessary to protect them. They use a combination
of [Flask JWT Simple](https://flask-jwt-simple.readthedocs.io/en/latest/index.html) and homegrown in
my lab, decorators. JWTs are generated, set with an expiry time and stored in the database. When 
users log out, these tokens are blacklisted.

# Environment variables
If you feel like it, before running things, you can definitely source environment variables in to
your shell from a [file and, they will be available to child processes](
https://stackoverflow.com/questions/19331497/set-environment-variables-from-file-of-key-value-pairs/19331521). 
This can be done like so: `set -a; source vars.txt; set +a`. But where is the fun in that?

Just use the [Manager](#manager) and it will load the correct environment variables from `.env`
files [here](configuration). Do make sure to ditch these and make your own ones that aren't
committed to Git, as they are flush with secrets.

For example if you execute with a `dev` variable it will use the [dev.env](configuration/dev.env)
file along with the [common.env](configuration/common.env) file.

## Testing
Testing is based on a [ThoughtWorks](https://www.thoughtworks.com) document called 'Testing
Strategies in a Microservice Architecture'
[published on Martin Fowler's blog](https://martinfowler.com/articles/microservice-testing/). The
article is about how to apply the Testing Pyramid to microservices. 
![Fowler Microservices Testing Summary](
bin/fowler-testing-microservices.png "Fowler Microservices Testing Summary")
I would highly recommend reading this. It's a very digestible and somewhat animated slide deck.

*I've applied the methods as much as I can without actually deploying the code to a real server.
That is out of scope for this experiment as I wanted to make this generic enough for any user. If
you're curious, I would most likely use [Zappa](https://github.com/Miserlou/Zappa) on
[AWS Lambda](https://aws.amazon.com/lambda), as I've had good success with that. Making a WSGI
server work on a serverless platform is some delightful black magic.*

I use the old favourite [pytest](https://docs.pytest.org).

Unit tests obviously don't require any special treatment.

Component tests use a combination of the Flask test client and an in-memory SQLite database. I know
SQLite can be a bit simple, but for these purposes I found it sufficient.

Integration tests are handled using a real Flask app and a [Postgres](https://www.postgresql.org)
Docker [container](https://hub.docker.com/_/postgres) which is launched using this
[docker-compose](tests/docker-compose.yml) file. This is the closest I could get to real, without
deploying to a real server.

Contract tests are basically the same functionality as the Component level, but with the
"integrationess" of the Integration tests.

There are no End-to-End tests. At some point I'd like to make a quick React front-end and introduce
these.

You can of course, run the tests using standard `pytest` commands, but I've written some nice
helpers which I would recommend using instead. See the [Test Runner section](#test-runner) and
[Manager section](#manager) below.

## Dev Tools
Being an industrious little ~~work avoiding~~ efficiency-creating developer, I'm quite the fan of
writing little helpers to make my working life ~~more filled with drinking coffee in the sun while
reading a book~~ easier. To run these, have a read of the [Manager section](#manager) below.

### Email
I needed to test things that require email such as user registration or password resets. Did I want
to set up a real email server to do this? That sounds an awful lot like a terrible slice of not fun
pain. Did I want to just skip testing this? Yes, yes I did, testing email sucks. Instead, I built an
extremely brilliant and highly robust 25 line long [email server](tools/email_server.py). This
little email server that could, is subclassed from the `DebuggingServer` from the `smtpd` built-in
library (thanks Guido). It intercepts the email, parses it, then dumps it to a local file where the
test suite can grab the auth tokens and be happy and `assert`ive.

### Postman
What if I told you that someone else had written a tool that converts your automatically generated
Swagger API into a [Postman](https://www.postman.com) collection, so you don't have to? Flask-RESTX
does that, so I didn't even need to. But, when I import that collection into Postman to do some
local API testing during development, there's a few things missing that I have to make myself.

First, I'd like an environment file. I want a pre-written collection of all the variables that I
use. Second, I want JavaScript snippets to process data from responses and dump those into
variables. For example, when the API sends back an auth token, I don't want to copy and paste that
into the headers for an endpoint like some sort of cave man. Enter, the
[Postman Creator](tools/postman_creator.py). Run it, and you'll find that the collection and
environment files you deserve will be waiting for you. Import these into Postman and never
copy-paste again. Also, you know you love it when some
[JavaScript is written in a Python script](tools/postman_config.py).

### Test runner
Testing is essential right? So you run your tests all the time right? You don't just wait until
you've committed them, and the build server runs them right? You make a change to your code, then
you run the tests locally right?

Ha ha I know, good one right?

Wrong.

In this little here project you can run the whole test suite from a
[single script](tools/test_runner.py). It loads all your environment variables (see
[above](#environment-variables)) before execution. First it runs the non-integrated tests i.e. Unit
and Component, then it runs a "deployed" version against a "real" database. We get the Flask app up
and running, we start the Docker database container. We even get Linting, Cyclomatic Complexity and
how many Logical Lines of Code are in the project.

You're welcome.

You want more? Okay fine, you can also use this on your build server instead of configuring that,
like I do on [Gitlab](.gitlab-ci.yml).

Bonus!
It generates those lovely badges, so you can show off that you have 142% coverage, 10,042 lines of
code and A+++++++++++ Cyclomatic Complexity.

### Static Code Analysis
As discussed above, there's a [helper](tools/static_code_analysis.py) for making badges for your
GitLab/GitHub etc. profile. This parses the results from [Pylint](https://www.pylint.org) and
[Radon](https://radon.readthedocs.io) and plugs them in to
[Anybadge](https://pypi.org/project/anybadge).

## Manager
Okay all of this sounds great. But, I don't really want to figure out how to get all this junk
running. Can't you make it easier for me?

Fine.

Here is the [script you've been searching for all your life](api_skeleton.py). This chap brings it
all together and gives you a nice API for your API. Using the power of the command line and
[Click](https://click.palletsprojects.com), you can start and stop the Flask app and the Postgres
database. You can set up a fresh database, or you can tear it down. You can even migrate from one
version to another if that tickles your fancy. I'm not here to judge you. You can run integrated
tests and if you like that, you'll love being able to run non-integrated tests. What's that you say?
You want to run static code analysis because you're a Pylint nerd like me? I got you. And as if that
wasn't enough, if you need those Postman files, the gang's all here. Oh and an email server. Yawn.

This loads all the correct environment variables (see [above](#environment-variables)), so you don't
have to.

To use the Manager script run
```bash
python api_skeleton.py <command> <options>
```

For example if you want to start the Flask app with the development config:
```bash
python api_skeleton.py run --environment dev
```

Or to run the integrated test suite:
```bash
python api_skeleton.py test --integrated true
```

To see all the available commands, and their respective options:

Functions in the Manager file that are decorated with `@cli.command()`, take their command from the
function name. For example `def postman()` becomes `postman` on the command line. If the decorator
`@click.option` is present, those are your command line options (and become the argument to the
function). In other words, `def test(integrated)` becomes `test --integrated` and the choices are
set in the decorator `type=click.Choice(['true', 'false'])`.

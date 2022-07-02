## Intro

This is a CLI tool designed to make it easier to interact with Small Improvements. It can be particularly helpful for managers to add talking points to multiple directs at once. Here is a quick example of what it looks like:

![](https://zappy.zapier.com/79070AFA-BDF5-4DF3-87D7-C1394412549E.png)

## Install

Requires Python 3.6+

1. Clone the repo `git clone git@github.com:bcooksey/small-improvements-cli.git`
1. `cd small-improvements-cli`
1. Install with pip/pip3, whichever is configured for Python 3 on your system  `pip3 install .`
1. Go to [Personal Access Tokens Page](https://www.small-improvements.com/app/personal-access-tokens) and generate an access token. Note: If you use a subdomain, visit `https://<subdoman>.small-improvements.com/app/personal-access-tokens`
1. Run `export SI_TOKEN=<your_token>` on your shell (and optionally add it to your ~/.bashrc)
1. `small-improvements setup`

## Common Usage

**Add a talking point. Will be prompted to type the talking point and which teammates to add it to.**

`small-improvements ap`

**Quickly add a talking point to a teammate.**

`small-improvements ap -t Bob This is a talking point`

**Add a private note to a meeting. Will open your default text editor to compose the note.**

`small-improvements add-note -p`

**Add a nickname to a teammate so you can select them by nickname instead of full name.**

`small-improvements add-nickname`

**Get help on adding a talking point**

`small-improvements ap --help`

## Pro Tips

If you are a manager with a lot of direct reports and you want to reduce who shows up in your list of folks, you can manually edit the `~/.small-improvements-cache` file to be just the reports you want to see.

## Development

Requires Python 3.6+

1. `python3 -m venv env`
1. `source env/bin/activate`
1. `pip install -r requirements.txt`
1. `python commands.py`

To run the tests

`./run_tests.sh`

A quick note on testing. The tests use two helper classes to make testing easier:

* A mock SI client that returns hard-coded data
* A cache that is memory backed instead of disk-backed. This allows for easy read/write without touching the filesystem

## References

[Small Improvements API Docs](https://storage.googleapis.com/si-rest-api-docs/dist/index.html)

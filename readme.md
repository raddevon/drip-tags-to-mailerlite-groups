# Drip Tags to MailerLite Groups converter

Takes your `people.csv` exported from Drip and, using the MailerLite API, adds your subscribers to groups matching their Drip tags.

## Installation

I used Poetry for environment isolation. If you want to do the same, run `poetry install` in the project root.

I've also provided a `requirements.txt` file in case you want to run the script the old fashioned way. Run `pip install -r requirements.txt` from the project root.

Add a file named `.env` to the project root specifying your MailerLite API key. The file should look something like this:

```bash
MAILERLITE_KEY="<replace-with-your-key>"
```

## Usage

It's very simple.

1. Place your `people.csv` in this directory
1. Run the script
   - If you're using Poetry, run `poetry run python create-groups.py`
   - If not, run `python create-groups.py`

## Notes

- This looks for a column in `people.csv` with the heading "tags" which is a column containing a CSV with all the user's tags. If any of this changes, the script won't work.
- If you forget to set `MAILERLITE_KEY` before you run this, it will fail.
- Not sure if Drip allows commas in tag names, but if they do, this script won't support that.
- This script will create users that don't exist. This isn't because of a choice I made in writing the script. It's just the way the MailerLite API works. When you add an email address to a group that doesn't yet belong to a subscriber, that subscriber gets created.

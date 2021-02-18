# Re-ls

Re-ls is a refresh/rehash of the traditional `ls` command.  It provides behavior similar to `ls`, but also offers an optional web UI for folder navigation.

## Installation

Re-ls is written in python3, and has not been compiled as of yes, so the first step may be to install python.

1. Ensure that you have python installed, with version >=3.6
2. Clone this repo
3. Run `pip install -r requirements.txt` from the command line after navigating into the cloned repo

## Usage

### CLI

Run
```
python src/rels.py
```

Add `--help` to see help
Add `-r`/`--recurse` to calculate the true directory size.  Expect the command to take some time if ran on large directories ('large' in this case referring to the number of child files)

### UI

right now the UI can only be initialized from the command line

Run
```
python src/rels.py --serve
```


## TODO for production readiness
 - Have a discussion with the intent team about the project
   - Talk about performance constraints, especially on directories like the root Directory
 - Find an alternative to the reprint package
   + It has cross platform capabilities
   + It's super simple to implement
   + It can consistently print a table without loosing sync on linecount (an issue I was facing while trying to build an alternative)
   - It has performance issues
   - It does not support large directories (that do not fit on the terminal)
   - It does not handle cases where the width of the table does not fit in the terminal
 - Better error handling in the UI
 - Add UI features to signify when folders are still loading vs. fully loaded
 - Optionally add out additional features
   - The API support for sorting by other columns and by selecting sort direction, however the UI does not surface these capabilities
   - The `Last Modified` column only records the last modified date of folders, but this could be very easily updated to return the max last modification time of any of it's children - which would argue may be more practical for some intents
 - Add more unit tests
 - Add Integration tests
 - Compile Flask for production
 - Compile Vue for production
 - Add setup.py and register package to an artifact repository like pypi
 - Could host this repo on AWS CodeCommit and integrate AWS CodePipeline to auto deploy the package
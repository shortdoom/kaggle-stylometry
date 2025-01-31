# kaggle-stylometry

A CLI version of Kaggle competition code.

Project got an Honorable Mention on Kaggle competition! https://www.kaggle.com/competitions/gemini-long-context/discussion/552419

Original notebook: https://www.kaggle.com/code/blackbigswan/github-profile-chat-analysis-and-insights

# Install & Run

In the new python virtual environment (`venv`):

`pip install -r requirements.txt`

This will also install [`gh-fake-analyzer`](https://pypi.org/project/gh-fake-analyzer) package required to build the GitHub profile report data and download all of the repositories source code. File `config.ini` is set appropriately to help with that task.

From within the same directory, run:

`gh-analyze <username>`

This will dump <username> github profile, together with repositories source code, to newly created /out/<username> directory.

Set the `.env` file

```sh
GH_TOKEN=<GITHUB_API_TOKEN>
GEMINI_API_KEY=<GOOGLE_GEMINI_LLM_API_KEY>
```

Then, you can use 

`python main.py <username>` to run the stylometric analysis.

# Note

Analysis takes about 15 minutes for standard accounts (individuals, regular contributors, but not above average). Unstable for bigger accounts. 

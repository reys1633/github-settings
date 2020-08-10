# GitHub Settings

This GitHub App syncs repository settings defined in `settings.yml` to GitHub.

## Prerequisites
This app requires python. Versions confirmed to work: 3.6.6 <br />
To install the required pyyaml, configobj, and request library, run `pip install pyyaml configobj request`. <br />

## Usage

1. Clone this repository into some directory
1. Edit the `settings.yml` file in the cloned directory. Changes to this file will be synced to GitHub.
1. From the command line in the cloned directory execute: <br /> ```python github-settings.py https://github.com/repo1/url https://github.com/repo2/url ...``` <br />
Each argument is the url to a GitHub repository for these settings to be applied to.
1. Enter personal access token when prompted. If you do not have a token, you can create one in GitHub developer settings by following [these instructions](https://docs.github.com/en/enterprise/2.21/user/github/authenticating-to-github/creating-a-personal-access-token)..

### Notes For settings.yml file
1. All top-level settings are optional. Some plugins do have required fields. See settings-example.yml for all possible settings.
1. Each top-level element under branch protection must be filled (eg: `required_pull_request_reviews`, `required_status_checks`, `enforce_admins` and `restrictions`). If you don't want to use one of them you must set it to `null` (see comments in the example above). Otherwise, none of the settings will be applied.
1. Example of all available settings with comments and links for further guidance can be found in [settings-example.yml](./settings-example.yml).
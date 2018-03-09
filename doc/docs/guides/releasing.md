# Making a Release
1. Tag the HEAD of the release branch and push to github: `git tag <version> && git push --tags`

1. Check version is correct in `_version.py`.

1. Make sure you have `twine` installed and then: `make release`

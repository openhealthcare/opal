# Making a Release

1. Tag the HEAD of the release branch and push to github: `git tag <version> && git push --tags`.
Opal branch names are in the format `vX.Y.Z` the tag for a release should be the `X.Y.Z` component
of the branch name.

1. Check version is correct in `_version.py`.

1. Make sure you have `twine` installed and then: `make release`

1. Merge the branch you are releasing into `master`

1. Update the Github release page and make sure that it has the relevant Changelog contents.

1. If the branch for the next version does not already exist, create that branch. For instance, if you
have released `x.y.z` then create `x.y.(z+1)`. If you are creating a new version branch, ensure you have
also changed the version number in the documentation, `opal._version.__version__`, and the branches that
any badges in the project README are pointing at.

1. Change the github default branch to be the new in development version

1. Update the Opal website: Change the current release and development version on the homepage, and run
`rake docs` to regenerate the documentation site with a new latest stable release version.

1. Post to the Opal mailing list to announce the new release.

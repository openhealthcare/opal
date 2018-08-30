# Making a Release
1. Make and deploy a version to test it on a windows machines.

2. Tag the HEAD of the release branch and push to github: `git tag <version> && git push --tags`.
Opal branch names are in the format `vX.Y.Z` the tag for a release should be the `X.Y.Z` component
of the branch name.

3. Check version is correct in `_version.py`.

4. Make sure you have `twine` installed and then: `make release`

5. Merge the branch you are releasing into `master`

6. Update the Github release page and make sure that it has the relevant Changelog contents.

7. If the branch for the next version does not already exist, create that branch. For instance, if you
have released `x.y.z` then create `x.y.(z+1)`. If you are creating a new version branch, ensure you have
also changed the version number in the documentation, `opal._version.__version__`, and the branches that
any badges in the project README are pointing at.

8. Change the github default branch to be the new in development version

9. Update the Opal website: Change the current release and development version on the homepage, and run
`rake docs` to regenerate the documentation site with a new latest stable release version.

10. Post to the Opal mailing list to announce the new release.

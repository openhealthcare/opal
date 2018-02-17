## Contributing to Opal

Opal is developed as an open source project, and as such we welcome contributions in the form of bug reports, documentation, and code.

### Reporting bugs

If you find what looks like a bug, add an issue to the [Github Issue tracker](https://github.com/openhealthcare/opal/issues).

Unclear documentation, unexpected error messages definitely count as bugs - feel free to raise issues about them.

Please try to include steps to reproduce your bug in the issue - it helps us enormously to find and fix it.

### Contributing enhancements or fixes

If you want to contribute an enhancement or fix to Opal:

* Fork the project on Github
* Make a feature branch from the latest default branch (this will be named vX.Y.Z and set as the default branch on Github)
* Make your changes
* Make sure that our test suite still runs, and that your changes are covered by tests (running `opal test -c` in the root directory of the repository will
run both python and javascript tests, as well as generate HTML code coverage reports.)
* Update the Opal documentation to be
* Commit the changes and push to your fork
* Submit a pull request to Opal

At this stage, we will assign someone to review your changes before merging. We might ask you to make some changes to your pull request before
merging, but in general, we are biased towards accepting contributions from the community.

That said, we won't merge your pull request if:

* It doesn't come with tests
* It doesn't update the relevant documentation

Don't worry though - we're happy to guide new contributors through this process.

If you want to discuss ideas you have for changes before making them, you can always propose enhancements on
the [Github Issue tracker](https://github.com/openhealthcare/opal/issues) or post questions and open discussions on the
[mailing list](https://groups.google.com/forum/?ohc-dev#!forum/ohc-opal).

### Issues suitable for new contributors

Issues in the github issue tracker labelled 'easy' have been identified as particularly appropriate for new contributors.

Changelog
---------

1.0.0 (October 12, 2024)
+++++++++++++++++++++

- Upgrade Mermaid to 11.2.0
- Add support for ELK diagrams
- Add support for name parameter
- Add passthrough of mermaid frontmatter
- Convert to native namespace package
- Drop support for Python 3.7
- Convert default placeholder from div to pre
- Fix for tempfile encoding when containing non ascii characters
- Fix for mermaid sequence config arguments
- Default to jsdelivr (previously unpkg) for JS asset CDN

See full `set of changes <https://github.com/mgaitan/sphinxcontrib-mermaid/compare/1.0.0...0.9.2>`_.


0.9.2 (May 28, 2023)
+++++++++++++++++++++

- Implemented zoom on diagrams functionality. Contributed by `Daniel Althviz Moré <https://github.com/dalthviz>`_
- Fix a bug on empty diagram generations. Contributed by `Kevin Deldycke <https://github.com/kdeldycke>`_.  
- Upgrade default to Mermaid 10.2.0. 
- Implement automatic releases from Github Actions when a tag is pushed 

See full `set of changes <https://github.com/mgaitan/sphinxcontrib-mermaid/compare/0.9.2...0.8.1>`_.


0.8.1 (Feb 25, 2023)
+++++++++++++++++++++

- Default to Mermaid 9.4.0 as 10.0 introduced incompatible changes. 
  See `the discussion <https://github.com/mermaid-js/mermaid/discussions/4148>`_. 

0.8 (Feb 9, 2023)
+++++++++++++++++++++

- Moved CI to Github Actions
- Make the class diagram reproducible
- Allow the user to change the JS priority
- Drop support for Python 3.6
- Black formatting

See `full set of changes <https://github.com/mgaitan/sphinxcontrib-mermaid/compare/0.7.1...0.8>`_.


0.7.1 (July 17, 2021)
+++++++++++++++++++++

- Update docs and tests for markdown support


0.7 (May 31, 2021)
++++++++++++++++++++++++++

- Add compatibility with Sphinx 4.0
- `mermaid_init_js` is now included in an standard way.
- Documented how to use in Markdown documents


0.6.3 (February 21, 2021)
++++++++++++++++++++++++++

- Make it compatible with recent Sphinx versions
- Add basic (real) tests (So I stop breaking it!)


0.6.2 (February 18, 2021)
++++++++++++++++++++++++++

- fix regression
- setup travis


0.6.1 (February 8, 2021)
++++++++++++++++++++++++++

- Fix a problem when called mermaid-cli
- Fix typos on documentation
- Improve internal code formatting (via black)

0.6.0 (January 31, 2021)
++++++++++++++++++++++++++

- Drop support for Python version older than 3.6.
- Allow to include javascript lib locally
- Initialization code is now customizable
- The default version included from the CDN is always the latest available.


0.5.0 (September 24, 2020)
++++++++++++++++++++++++++

- Added mermaid_cmd_shell. Useful for Windows user.
- Reimplement inheritance diagrams.
- Fix UnicodeEncodeError on Python 2

0.4.0 (April 9, 2020)
+++++++++++++++++++++

- Added `mermaid_params`
- Added config file option
- Improved latex integration
- Added the `pdfcrop` functionality
- Mermaid version is configurable
- Several cleanups in the code


0.3.1 (Nov 22, 2017)
++++++++++++++++++++

- Support the new Mermaid CLI by `Bastian Luettig <https://github.com/bastiedotorg>`_


0.3 (Oct 4, 2017)
+++++++++++++++++++

- several improves and bugfixes contributed by `Alberto Berti <https://github.com/azazel75>`_

0.2.1 (Jun 4, 2017)
+++++++++++++++++++

-  Workaround for opacity issue with rtd's theme (thanks to `Anton
   Koldaev <http://github.com/iroller>`_)

0.2 (Jun 4, 2017)
+++++++++++++++++

-  Python 3 support fix (thanks to `Shakeeb
   Alireza <http://github.com/shakfu>`_)
-  In-browser diagram generation
-  Autoclasstree directive. (Thanks to
   `Zulko <http://github.com/zulko>`_)

0.1.1 (Jun 4, 2017)
+++++++++++++++++++

-  Better usage instructions
-  Bugfix

0.1 (Jul 18, 2016)
++++++++++++++++++

-  first public version

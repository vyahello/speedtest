![Screenshot](logo.png)

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with pylint](https://img.shields.io/badge/pylint-checked-blue)](https://www.pylint.org)
[![Checked with flake8](https://img.shields.io/badge/flake8-checked-blue)](http://flake8.pycqa.org/)
[![Checked with pydocstyle](https://img.shields.io/badge/pydocstyle-checked-yellowgreen)](http://www.pydocstyle.org/)
[![Checked with interrogate](https://img.shields.io/badge/interrogate-checked-yellowgreen)](https://interrogate.readthedocs.io/en/latest/)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.md)
[![EO principles respected here](https://www.elegantobjects.org/badge.svg)](https://www.elegantobjects.org)

## Speedtest

Small, fast **network speedtest CLI utility** written in Python.

It measures:
- **Latency + jitter** (multiple quick HTTP requests)
- **Download speed**
- **Upload speed**

By default it tests against Cloudflare’s public speedtest endpoints:
`https://speed.cloudflare.com/__down` and `https://speed.cloudflare.com/__up`.

## Tools

### Production

- python **3.10+**

### Development

- [pytest](https://pypi.org/project/pytest/)
- [black](https://black.readthedocs.io/en/stable/)
- [mypy](http://mypy.readthedocs.io/en/latest)
- [pylint](https://www.pylint.org/)
- [flake8](http://flake8.pycqa.org/en/latest/)
- [pydocstyle](https://github.com/PyCQA/pydocstyle)

## Usage

### Quick start

Install editable (recommended for development):

```bash
pip install -e . -r requirements-dev.txt
```

Run (default profile: **standard**, more realistic / slightly longer):

```bash
speedtest
```

Or:

```bash
python -m speedtest
```

JSON output:

```bash
speedtest --json
```

Adjust test sizes (bytes):

```bash
speedtest --download-bytes 20000000 --upload-bytes 8000000
```

Profiles:

```bash
speedtest --profile fast
speedtest --profile medium
speedtest --profile standard
speedtest --profile extended
```

## Development notes

### Testing

Generally, `pytest` tool is used to organize testing procedure.

Please follow next command to run unittests:
```bash
pytest
```

### CI

CI runs on **GitHub Actions** and executes `./analyse-source-code.sh` on Python 3.10–3.14.

To run the same checks locally:
```bash
./analyse-source-code.sh
```
### Release notes

Please check [changelog](CHANGELOG.md) file to get more details about actual versions and it's release notes.

### Meta

Author – _Volodymyr Yahello_. Please check [authors](AUTHORS.md) file for more details.

Distributed under the `MIT` license. See [license](LICENSE.md) for more information.

You can reach out me at:
* [vyahello@gmail.com](vyahello@gmail.com)
* [https://x.com/vyahello](https://x.com/vyahello)
* [https://www.linkedin.com/in/volodymyr-yahello](https://www.linkedin.com/in/volodymyr-yahello)

### Contributing
I would highly appreciate any contribution and support. If you are interested to add your ideas into project please follow next simple steps:

1. Clone the repository
2. Configure `git` for the first time after cloning with your `name` and `email`
3. `pip install -r requirements.txt` to install all project dependencies
4. `pip install -r requirements-dev.txt` to install all development project dependencies
5. Create your feature branch (git checkout -b feature/fooBar)
6. Commit your changes (git commit -am 'Add some fooBar')
7. Push to the branch (git push origin feature/fooBar)
8. Create a new Pull Request

### What's next

All recent activities and ideas are described at project [issues](https://github.com/vyahello/speedtest/issues) page. 
If you have ideas you want to change/implement please do not hesitate and create an issue.

**[⬆ back to top](#speedtest)**

<p align="center">
  <img src="https://github.com/Emmanuelpean/jam/blob/main/frontend/assets/Logo.svg" alt="Jam" width="150">
</p>

<h1 align="center">JAM</h1>
<h2 align="center">Job Application Manager</h2>

<div align="center">

  [![Passing](https://github.com/Emmanuelpean/jam/actions/workflows/test.yml/badge.svg?branch=main&event=push)](https://github.com/Emmanuelpean/jam/actions/workflows/test.yml)
  [![Tests Status](./reports/tests/tests-badge.svg?dummy=8484744)](https://emmanuelpean.github.io/jam/reports/tests/report.html?sort=result)
  [![Coverage Status](./reports/coverage/coverage-badge.svg?dummy=8484744)](https://emmanuelpean.github.io/jam/reports/coverage/htmlcov/index.html)
  [![Last Commit](https://img.shields.io/github/last-commit/emmanuelpean/jam/main)](https://github.com/emmanuelpean/jam/commits/main)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

</div>

*Jam* is a user-friendly web app designed to give you a quick look at your data without needing to write a single line 
of code or spend time reformatting files. It supports a wide range of data file formats and takes care of the behind-
the-scenes work of reading and processing the data, so you can jump straight to visualising and exploring your results.

The idea came from a simple frustration: too often, valuable time is lost just trying to open and make sense of a data 
file. This app removes that barrier. Whether you are checking raw instrument output, exploring simulation results, or 
comparing experimental datasets, it lets you plot and inspect the data in just a few clicks. It is especially handy in 
fast-paced research environments where quick decisions depend on a fast understanding of the data.

## Installation

Create and activate a virtual environment, and run:
```console
$ pip install -e .[dev]
```

## Usage
To run the app locally on Windows, run:
```console
$ ./run.bat
```

On Mac OS:
```console
$ ./run.sh
```

# Online Judgement CLI

[![Tests](https://github.com/tokusumi/judge-cli/actions/workflows/test.yml/badge.svg)](https://github.com/tokusumi/judge-cli/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/tokusumi/judge-cli/branch/main/graph/badge.svg?token=ZK2SDRZNAN)](https://codecov.io/gh/tokusumi/judge-cli)

Forked from [Online-Judge-Tools/oj](https://github.com/online-judge-tools/oj)

## Install

Using Pip:

```sh
pip install git+https://github.com/tokusumi/judge-cli.git
```

## Testing

Download test case from contest site and testing them, powered by `online-judge-api-clients`.

### Configuration

```sh
mkdir a && cd a
judge conf -ii
```

You can enter required values interactively as follows:

```sh
$ judge conf -ii

file:
contest: abc188
problem: a
URL [https://atcoder.jp/contests/abc188/tasks/abc188_a]:
testdir [/home/user/wsl2/Work-atcoder/abc-188/a/tests]:
Are you sure to save the following configurations?
workdir = /home/user/wsl2/Work-atcoder/abc-188/a
URL = https://atcoder.jp/contests/abc188/tasks/abc188_a
contest = abc188
problem = a
testdir = /home/user/wsl2/Work-atcoder/abc-188/a/tests
py = True
pypy = False
cython = False
mle = 256.0
tle = 2000.0
mode = CompareMode.EXACT_MATCH
verbose = VerboseStr.error_detail
 [yes]: 
Success for configuration.
```

See more details by ```judge conf --help```.

### (Optional) Download test cases

Testcases you set above will be downloaded:

```sh
$ judge download
Load configuration...
Download https://atcoder.jp/contests/abc188/tasks/abc188_a
```

See more details by ```judge download --help```.

### Testing your script

Testing as follows (solution file (ex: `a.py`) is required):

```sh
$ judge test -f a.py
Load configuration...
Check for test cases...

Testing a.py for tests...

execution versions:


Testing python3...

=====================================================
slowest: 10.00 ms (for sample-u1)
max memory: 8.45 MB (for sample-1)
Success: 3 AC / 3 cases
```

Note: if you've not downloaded system testcases, you have a chance to download them here.

See more details by ```judge test --help```.

### Add user testcase

Call as follows:

```sh
$ judge add
Load configuration...
Add testcase for /home/user/wsl2/Work-atcoder/abc-188/a/tests
Check for test cases...
Created: sample-u1
```

Then, new brank test sample files (sample-u*.in and sample-u*.out). Write test values into them.

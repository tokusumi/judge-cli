# Online Judgement CLI
[![Tests](https://github.com/tokusumi/judge-cli/actions/workflows/test.yml/badge.svg)](https://github.com/tokusumi/judge-cli/actions/workflows/test.yml)


Forked from [Online-Judge-Tools/oj](https://github.com/online-judge-tools/oj)

## Install

Using Pip:

```sh
$ pip install git+https://github.com/tokusumi/judge-cli.git
```

## Testing

Download test case from contest site and testing them, powered by `online-judge-api-clients`.

### Download test cases

For example:

```sh
judge download abc051 b
```

See more details by ```judge download --help```.

### Testing your script

Testing as follows:

```sh
judge test abc_051_b.py abc051 b
```

See more details by ```judge test --help```.

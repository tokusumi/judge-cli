import contextlib
import http.cookiejar
import os
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import Generator, Iterator, List, Optional

import onlinejudge.dispatch as dispatch
import onlinejudge.utils as utils
import pkg_resources
import requests
from onlinejudge.service.yukicoder import YukicoderProblem
from onlinejudge.type import Problem, SampleParseError, TestCase
from requests.exceptions import InvalidURL
from typing_extensions import Literal

from judge.schema import Sample
from judge.tools.format import embedd_percentformat


def url_from_contest(contest: str, problem: str) -> str:
    url = f"https://atcoder.jp/contests/{contest}/tasks/{contest}_{problem}"
    return url


@contextlib.contextmanager
def create_UA_session(
    *, path: Path, token: Optional[str] = None
) -> Iterator[requests.Session]:
    """create new session with our User-Agent"""
    session = requests.Session()
    pkg = pkg_resources.get_distribution("judge")
    try:
        url = __url__  # type: ignore
    except NameError:
        url = ""
    session.headers["User-Agent"] = "{}/{} (+{})".format(
        pkg.project_name, pkg.version, url
    )
    if token:
        session.headers["Authorization"] = f"Bearer {token}"
    try:
        with utils.with_cookiejar(session, path=path) as session:
            yield session
    except http.cookiejar.LoadError:
        raise


@dataclass
class DownloadArgs:
    cookie: Path = utils.default_cookie_path
    system: bool = False
    url: Optional[str] = None
    contest: Optional[str] = None
    no: Optional[str] = None
    problem: Problem = field(init=False, repr=True)
    token: Optional[str] = None

    def __post_init__(self) -> None:
        if self.url:
            url = self.url
        elif self.contest and self.no:
            url = url_from_contest(self.contest, self.no)
        else:
            raise ValueError("required url or pairs of contest and no")
        problem = dispatch.problem_from_url(url)
        if not problem:
            raise InvalidURL('The URL "%s" is not supported' % url)
        self.problem = problem

        if not isinstance(self.problem, YukicoderProblem):
            self.token = None


@dataclass
class SaveArgs:
    format: str
    directory: Path


def get_extensions() -> Generator[Literal["in", "out"], None, None]:
    yield "in"
    yield "out"


def testcases_to_samples(
    testcases: List[TestCase], format: str, directory: Path
) -> Generator[Sample, None, None]:
    _filename = embedd_percentformat(format)
    for idx, testcase in enumerate(testcases):
        for ext in get_extensions():
            data = getattr(testcase, ext + "put_data")
            if data is None:
                continue
            path = directory / _filename.format(
                i=str(idx + 1),
                e=ext,
                n=testcase.name,
                b=os.path.basename(testcase.name),
                d=os.path.dirname(testcase.name),
            )
            yield Sample(
                ext=ext,
                path=path,
                data=data,
            )


def download(args: DownloadArgs) -> List[TestCase]:
    # download samples
    with create_UA_session(path=args.cookie, token=args.token) as sess:
        if args.system:
            testcases = args.problem.download_system_cases(session=sess)
        else:
            testcases = args.problem.download_sample_cases(session=sess)
    if not testcases:
        raise SampleParseError("Sample not found")
    return testcases


def save(testcases: List[TestCase], args: SaveArgs) -> None:
    get_samples = partial(testcases_to_samples, testcases, args.format, args.directory)
    # TODO: append the history for submit subcommand

    # raise if new sample overwrides existing files
    for sample in get_samples():
        if sample.path.exists():
            raise FileExistsError(
                "Failed to download since file already exists: " + str(sample.path)
            )

    # save samples
    for sample in get_samples():
        sample.path.parent.mkdir(parents=True, exist_ok=True)
        with sample.path.open("wb") as fh:
            fh.write(sample.data)

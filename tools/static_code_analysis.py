import contextlib
import os

import anybadge
from pylint.lint import Run
from radon.cli import CCHarvester, Config, RawHarvester
from radon.complexity import SCORE

from app.utils import FIRST


class StaticCodeAnalysis:

    @property
    def _paths(self):
        return ['app']

    @property
    def _analyser(self):
        raise NotImplementedError('Subclasses should implement this')

    @property
    def _thresholds(self):
        raise NotImplementedError('Subclasses should implement this')

    def run_test(self):
        raise NotImplementedError('Subclasses should implement this')

    def create_badge(self, score):
        badge = anybadge.Badge(
            self._analyser, score, thresholds=self._thresholds, value_prefix=' ', value_suffix=' '
        )
        filename = self._analyser.replace(' ', '-')
        analyser_svg = f'{filename}.svg'
        with contextlib.suppress(FileNotFoundError):
            os.remove(analyser_svg)
        badge.write_badge(analyser_svg)


class Lint(StaticCodeAnalysis):

    @property
    def _analyser(self):
        return 'pylint'

    @property
    def _thresholds(self):
        return {
            2: 'red',
            4: 'orange',
            6: 'yellow',
            10: 'green',
        }

    def run_test(self):
        results = Run(['app'], do_exit=False)
        score = round(results.linter.stats['global_note'], 2)
        return score


class CyclomaticComplexity(StaticCodeAnalysis):

    @property
    def _analyser(self):
        return 'cyclomatic complexity'

    @property
    def _thresholds(self):
        return {
            'F': 'red',
            'E': 'red',
            'D': 'red',
            'C': 'orange',
            'B': 'yellow',
            'A': 'green',
        }

    @property
    def _config(self):
        return Config(
            exclude=None,
            ignore=None,
            order=SCORE,
            no_assert=False,
            show_closures=False,
            average=True,
            total_average=True,
            show_complexity=True,
            min='A',
            max='F',
        )

    def run_test(self):
        harvester = CCHarvester(self._paths, self._config)
        # Weird ripping apart of iterators because to_terminal() seems to be the only way to get the
        # overall average. And it is only returned through iterators. Maybe I should do a pull
        # request to the project.
        *_, last = harvester.to_terminal()
        _, mid, _ = last
        _, score, *_ = mid
        return score


class LogicalLinesOfCode(StaticCodeAnalysis):

    @property
    def _analyser(self):
        return 'logical lines of code'

    @property
    def _thresholds(self):
        return {
            0: 'green',
        }

    @property
    def _config(self):
        return Config(
            exclude=None,
            ignore=None,
            summary=True,
        )

    def run_test(self):
        harvester = RawHarvester(self._paths, self._config)
        # This is horrible but the code wasn't designed to be used this way. This is parsing the
        # terminal output programmatically. I smells a pull request to the project.
        target_idx = 0
        lloc = 0
        for idx, item in enumerate(harvester.to_terminal()):
            if item[FIRST] == '** Total **':
                target_idx = idx + 2
            if target_idx == idx:
                lloc = item
        score = lloc[1][1]
        return score

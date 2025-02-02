from argparse import Namespace
from .action import Action
from inputparser import Parser
from recurrences import RecBuilder
from symengine.lib.symengine_wrapper import sympify
from simulation import Simulator
from plots import StatesPlot, RunsPlot
from cli.common import get_moment
from program import normalize_program
from inputparser import parse_program
import settings


class PlotAction(Action):
    cli_args: Namespace

    def __init__(self, cli_args: Namespace):
        self.cli_args = cli_args

    def __call__(self, *args, **kwargs):
        benchmark = args[0]
        monom = sympify(self.cli_args.plot)
        first_moment = second_moment = None
        if self.cli_args.plot_expectation or self.cli_args.plot_std:
            program = parse_program(benchmark)
            program = normalize_program(program)
            rec_builder = RecBuilder(program)
            solvers = {}
            settings.numeric_croots = True
            settings.numeric_roots = True
            if self.cli_args.plot_std:
                second_moment, _ = get_moment(
                    monom**2, solvers, rec_builder, self.cli_args, program
                )
            first_moment, _ = get_moment(
                monom, solvers, rec_builder, self.cli_args, program
            )

        program = Parser().parse_file(benchmark)
        simulator = Simulator(self.cli_args.simulation_iter)
        result = simulator.simulate(program, [monom], self.cli_args.number_samples)
        if self.cli_args.states_plot:
            p = StatesPlot(
                result,
                monom,
                self.cli_args.anim_time,
                self.cli_args.max_y,
                first_moment,
                second_moment,
                is_probabilistic=program.is_probabilistic,
            )
        else:
            p = RunsPlot(
                result,
                monom,
                self.cli_args.yscale,
                self.cli_args.anim_iter,
                self.cli_args.anim_runs,
                self.cli_args.anim_time,
                first_moment,
                second_moment,
                is_probabilistic=program.is_probabilistic,
            )
        if self.cli_args.save:
            print("Rendering and saving plot")
            p.save("plot")
            print("Plot saved.")
        else:
            p.draw()

# Author: Pierre Schnizer <pierre.schnizer@helmholtz-berlin.de>
#
# Illustrating my view on chromaticity measurement
# The example is deliberatly verbose to explain general concepts
# the first part is very long and gives all details. The second
# part will explain how one could combine them to a "service"
#
# The first part is very much oriented to the architecture that
# vtk (KItware / Visualiastion Toolkit) and GSL do: many layers and
# objects that interact to achieve the task.
# The art is then to provide a tuned standard that works for many
# cases. The advantage is that a user can interact on many different
# levels depending on the task in question
#
# I see what is described in the specification splits up in many
# different tasks

# * measurements are described by commands: simple objects
# * command rewritter translates it between the different views
# * measurement execution engine executes the command on
#   the appropriate backend
# * an chromaticity oracle is used to forecast which correction
#   shall be applied. It gets the sextupoles to use next to their
#   response on instantiation: probably provided in data models made
#   available by a repo pattern
# * a stepper is set up that applies a certain step to the chromaticity
# * furthermore a driver is used to drive chromaticity step by step.
#   here one more oracle can be added: it allows the user to programmatically
#   configure which steps have to be made to get into it
#
# The second part tries to achieve what pyvista does:
# a simple interface for standard tasks.
#
# The objects above are arranged together in Facade. The average
# user will only interact with this object. If it works fine.
# If not the build up code gives a lot of places to interact with
# and build your own.
#
#
# I use here the name pamila instead of pyaml as I use  pycharm so that
# not too many problems will arise due to name clashes ...

from dataclasses import dataclass
from typing import Sequence

from pamila.data_model.command import Command, BehaviourOnError
# this could be of course within a core util package
from pamila.command_sequence_exporter import export_commands
from pamila.pre_processor import ChromaticityDataPreprocessor
from pamila.processor import ChromaticityProcessor
from pamila_bessyii.yellow_pages import BessyIIYellowPages as YP
from pamila_bessyii.liason_manager import LiasonManager
from pamila_bessyii.translation_service import TranslationService
from pamila_bessyii.repository import Repository
from pamila_bessyii.measurement_execution_engine import MeasurementExecutionEngine
from pamila_bessyii.data_broker import DataBroker
from pamila import CommandRewritter

# Repository as handle to the configuration data
# It has to be reviewed if a single repository can do the job. The idea
# is to have dedicated repositories for the different layers. As of today
# I see at least
#  * yellow pages: grouping of device identifiers
#  * liasion_management: how the different views are combined
#  * translation_services: how to translate these
#
# One more service could be caching etc ...
#
# now give the repository the handle we like to addreess
repo = Repository("the global_key_d_jour")
yp = YP(repo.get_yellow_pages_repository())

# Now let's establish the measurement plan

master_clock_id = yp.get("master_clock")
# This I would leave to the user ... its just a list comprehension
# alternatively user could choose to measure assmetrically etc ...
rf_step = 10 # Hz
measurement_values = [val * rf_step for val in range(5)]
cmds_on_lattice = [
    Command(
        # Here one should discuss if certain devices  / functionality
        # id should be the same for all centers. Currently, I assume it
        # is different per center
        id=master_clock_id, property="delta_frequency", value=val, behaviour_on_error=BehaviourOnError.stop
    )
    for val in measurement_values
]

# this could be also written to yaml or in a database etc
# one needs to revise if the export command should be a
# method of some databroker instance ...
with open("chroma_commands.json", "wt") as fp:
    export_commands(commands, fp)

# Now all that is left to get the "raw" measurement data
# alternatively one could have one implemented at a different step
# this example is perhaps not the best ...
# cavity frequency is directly modified.
# perhaps one should translate from some deltap to corresponding RF
# could it then be the same or similar for each light source
command_rewritter=CommandRewriter(
    liasion_manager=LiasonManager(repo.get_liason_management_repository()),
    translation_service=TranslationService(repo.get_translation_management_repository())
)

# I like to think of these as a "work plan" this is now rewritten to what is to
# be executed on the machine
cmds_on_machine = CommandSequence(
    commands=[
        command_rewritter.forward(cmd) for cmd in cmds_on_lattice.commands
    ]
)

# This should look very much like a bluesky run engine.
# Data are streams for me.
# I am hesitant to reinvent the wheel
# The measurement engine is responsible to talk to the proper implementation
# be it the machine, the twin or any other part
me = MeasurementExecutionEngine(
    # This part executes the commands ... yes for me that would be handled by
    # bluesky, but I think others can delegate that to other implementations
    # I think the run engine is is responsibe for streaming data.
    engine = RunEngine(),
)
# How data are handled and stored are part of the databroker
# I think something like an event_model will be required too
# I think that bluesky is a fit here ...
# but I don't need to inforce it here.
# all what is required that it accepts and executes the commands
#
me.subscribe(data_broker)
# The measurement execution engine
uid, = me.execute(cmds_on_machine)

# analysis part below
data = data_broker.get_data(uid)

# I use dataclasses to represent the result. All measurements are basically
# snap shots of a random variable typically represented by the first order
# momenta.
@dataclass
class MomentaOfRandomVariable:
    mean : float
    std: float

# coorindate system needs to be defined ... x,y,z is perhaps not the best choice
# as it is different at different labs ...
@dataclass
class ChromatictyMeasurement:
    x: MomentaOfRandomVariable
    y: MomentaOfRandomVariable
    z: MomentaOfRandomVariable


# data should be close to measurement data ... these need to be preprocessed
# and then analysed
# The idea is to build here a filter line vtk ... would connect them here
# I think that is too early to see if that's appropriate
#
# The preprocessor takes data from the event data stream and combines
# it so that chromaticity can be measured (e.g. removing spurious signals)
# combining them into the data model that the chromaticity processor expects
chroma_p = ChromaticityPreprocessor(repo.get_chromatistiy_preprocessor_repository())
chroma_pre_p = ChromaticityProcessor(repo.get_chromatistiy_processor_repository())


# The data result depend on which machine it was executed: real one,
# twin etc ...
# If required it should be available form the metadata on which machine
# it was calculated. Better a handle than anything else
# If you need another value all what should be required to use another uid...
chroma_real_world = chroma_p.process(chroma_pre_p.process(chroma_p.data_broker.get_data(uid)))
# Missing execution on the digital world
chroma_digital_calc = chroma_p.process(chroma_pre_p.process(chroma_p.data_broker.get_data(uid_calc)))

# The difference would then tell us what to do
dc = chroma_real_world - chroma_digital_calc

# correction requires different tools to work with
# * an oracle that can forecast the corrections to apply
# * and the measurement execution engine to implement it
class ChromaticityOracle:
    def ask(self, dc) -> Sequence[Command]:
        pass

# So now lets look into correction step by step
# This ChromaticityService could be handled
# I would model it similar to GSL stepper for ODE solvers
# Tell user which step you want to do etc
# Here a dedicated oracle could be used to define how
# to measure chromaticity at a given point
class ChormaticityStepperService:
    def __init__(self, *,
        me: MeasurementExecutionEngine,
        co: ChromaticityOracle,
        **kwargs
    ):
        pass

    def step(self, h) -> h:
        """one step closer to the chromaticity

        returns next step it would take
        """
        pass

# Then if you would like to have a fully automatic one, here you go
# this could be an object which is available at the machine
# this would also have a measurement execution engine. Here one has
# to see if one would like to have some oracle to forecast the
# range of measurement
# have a look to GSL ODE driver to get an idea which sort of parameters
# could be required
class ChromaticityDriverService:
    def __init__(self, *,
        stepper: ChromaticityStepperService,
        step_forcast: ChromaticityStepForecastService,
        oracle: ChromaticityOracle,
    ):
        pass

    def drive_to_target(self, target, n_steps):
        pass



# then to set the chromticity could be as simple as given below
cds = ChromaticityDriverService()
cds.drive_to_target(target)

# I rather would prefer to ask the user to loop over it ...
# then the user can inspect the next step if needed
# furthermore I'd prefer that is an asyncio one
for cnt, next_step in enumerate(cds.drive_to_target(target, h_max)):
    # Here a measurement could then be executed internally
    next_step = await next_step
    if cnt > max_steps:
        break

# given enough experience one could then put that all into one loop
dp_buzzer = cds.drive_to_target()
dp = await dp_buzzer

# ----------------------------------------------------------------
# This driver service could be instaniated for the user by the setup
# Not sure yet how to handle the different facility modes etc ...
#
# If that does all what you want fine ...
# If user is not happy, pamila_bessyii would give all the set up
# above. Then the user can chose which parts the user wants to
# replace by his/her desired feature.
from pamila_bessyii import chromaticity_driver_service_default as cdsd

# The precis
chroma = cdsd.measure()
residual_chroma = await cds.drive_to_target(chrome_desired)


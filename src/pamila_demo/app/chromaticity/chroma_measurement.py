from typing import Sequence

from bluesky import RunEngine
from databroker import catalog
from ophyd import Signal

from ...bl.set_command_rewriter import set_command_rewriter
from ...bluesky_measurement_execution_engine import BlueskyMeasurementExecutionEngine
from ...custom.epics.bluesky_measurement_engine import setup
from ...model.command import Command, BehaviourOnError, CommandSequence

def run(master_clock_id: str, measurement_values: Sequence[float]):
    # Now let's establish the measurement plan

    cmds_on_lattice = [
        Command(id=master_clock_id, property="delta_frequency", value=val, behaviour_on_error=BehaviourOnError.stop) for
        val in measurement_values]

    command_rewritter = set_command_rewriter()
    # I like to think of these as a "work plan" this is now rewritten to what is to
    # be executed on the machine
    cmds_on_machine = CommandSequence(commands=[command_rewritter.forward(cmd) for cmd in cmds_on_lattice])
    devices = setup(device_ids=tuple())
    tune_devices = devices["tunes"]
    master_clock = devices["master_clock"]
    RE = RunEngine()
    db = catalog["heavy_local"]
    RE.subscribe(db.v1.insert)

    md = {}
    info_sigs = {name: Signal(name=name) for name in ["device_name", "channel_name", "channel_value"]}
    if not master_clock.connected:
        master_clock.wait_for_connection(timeout=5)
    if not tune_devices.connected:
        tune_devices.wait_for_connection(timeout=5)
    stat = tune_devices.trigger()
    stat.wait(timeout=3)

    start_data = master_clock.read()
    start_data
    mexec = BlueskyMeasurementExecutionEngine(run_engine=RE)
    uid = mexec.execute(commands_collection=cmds_on_machine.commands,  # need to add bpms
                        detectors=[tune_devices], actuators=dict(master_clock=master_clock), info_signals=info_sigs,
                        md=md, )
    print(f"Run created {uid=}")

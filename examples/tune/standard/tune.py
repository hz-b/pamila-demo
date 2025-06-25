from pamila_demo.app.tune.tune_measurement import tune
from pamila_demo.bl.liasion_translator_setup import build_managers


if __name__ == "__main__":
    yp, _, _ = build_managers()
    tune(
        quadrupole_names=[name for name in yp.tune_correction_quadrupole_names()],
        measurement_values=[0, 1e-5, 0, -1e-5, 0]
    )
from pamila_demo.app.tune.tune_measurement import tune
from pamila_demo.bl.yellow_pages import yellow_pages

if __name__ == "__main__":
    yp = yellow_pages()
    tune(
        quadrupole_names=[name for name in yp.tune_correction_quadrupole_names()],
        measurement_values=[0, 1e-5, 0, -1e-5, 0]
    )
from pamila_demo.app.chromaticity.chroma_measurement import run
from pamila_demo.bl.yellow_pages import yellow_pages

if __name__ == "__main__":
    yp = yellow_pages()
    rf_step = 1
    run(
        master_clock_id=yp.get("master_clock"),
        measurement_values=[val * rf_step for val in range(5)]
    )

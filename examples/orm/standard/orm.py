from pamila_demo.app.orm.orm_measurement import orm
from pamila_demo.bl.yellow_pages import yellow_pages

if __name__ == "__main__":
    yp = yellow_pages()
    orm(
        horizontal_steerer_names=[name[1:] for name in yp.horizontal_steerer_names()],
        vertical_steerer_names=[name[1:] for name in yp.vertical_steerer_names()],
        measurement_values=[0, 1e-5, 0, -1e-5, 0]
    )
import plotly.graph_objects as go
import numpy as np


def plot_isosurface(grid, V, plot_option):
    dims_plot = plot_option.dims_plot
    idx = [slice(None)] * grid.dims
    slice_idx = 0

    dims_list = list(range(grid.dims))
    for i in dims_list:
        if i not in dims_plot:
            idx[i] = plot_option.slices[slice_idx]
            slice_idx += 1

    if len(dims_plot) == 2:
        dim1, dim2 = dims_plot[0], dims_plot[1]
        complex_x = complex(0, grid.pts_each_dim[dim1])
        complex_y = complex(0, grid.pts_each_dim[dim2])
        mg_X, mg_Y= np.mgrid[grid.min[dim1]:grid.max[dim1]: complex_x, grid.min[dim2]:grid.max[dim2]: complex_y]
        print("Plotting beautiful 2D plots. Please wait\n")
        fig = go.Figure(data=go.Contour(
            x=mg_X.flatten(),
            y=mg_Y.flatten(),
            z=V.flatten(),
            colorscale='jet'
        ))
        fig.show()
        print("Please check the plot on your browser.")

    elif len(dims_plot) == 3:
        dim1, dim2, dim3 = dims_plot[0], dims_plot[1], dims_plot[2]
        complex_x = complex(0, grid.pts_each_dim[dim1])
        complex_y = complex(0, grid.pts_each_dim[dim2])
        complex_z = complex(0, grid.pts_each_dim[dim3])
        mg_X, mg_Y, mg_Z = np.mgrid[grid.min[dim1]:grid.max[dim1]: complex_x, grid.min[dim2]:grid.max[dim2]: complex_y,
                           grid.min[dim3]:grid.max[dim3]: complex_z]

        my_V = V[tuple(idx)]

        if (V > 0.0).all() or (V < 0.0).all():
            print("Implicit surface will not be shown since all values have the same sign ")
        print("Plotting beautiful 3D plots. Please wait\n")
        fig = go.Figure(data=go.Isosurface(
            x=mg_X.flatten(),
            y=mg_Y.flatten(),
            z=mg_Z.flatten(),
            value=my_V.flatten(),
            colorscale='jet',
            isomin=plot_option.min_isosurface,
            surface_count=1,
            isomax=plot_option.max_isosurface,
            caps=dict(x_show=True, y_show=True)
        ))
        fig.show()
        print("Please check the plot on your browser.")

    else:
        raise Exception('dims_plot length should be equal to 2 or 3\n')


def plot_2d(grid, V_2D):
    dims_plot = [0, 1]
    dim1, dim2 = dims_plot[0], dims_plot[1]
    complex_x = complex(0, grid.pts_each_dim[dim1])
    complex_y = complex(0, grid.pts_each_dim[dim2])
    mg_X, mg_Y = np.mgrid[grid.min[dim1]:grid.max[dim1]: complex_x, grid.min[dim2]:grid.max[dim2]: complex_y]
    print("Plotting beautiful 2D plots. Please wait\n")
    fig = go.Figure(data=go.Contour(
        x=mg_X.flatten(),
        y=mg_Y.flatten(),
        z=V_2D.flatten(),
        zmin=0.0,
        ncontours=1,
        zmax=0.0,

    ))
    fig.show()
    print("Please check the plot on your browser.")


def plot_2d_with_map(grid, V_2D):
    dims_plot = [0, 1]
    dim1, dim2 = dims_plot[0], dims_plot[1]
    complex_x = complex(0, grid.pts_each_dim[dim1])
    complex_y = complex(0, grid.pts_each_dim[dim2])
    mg_X, mg_Y = np.mgrid[grid.min[dim1]:grid.max[dim1]: complex_x, grid.min[dim2]:grid.max[dim2]: complex_y]
    print("Plotting beautiful 2D plots. Please wait\n")
    fig = go.Figure(data=go.Contour(
        x=mg_X.flatten(),
        y=mg_Y.flatten(),
        z=V_2D.flatten(),
    ))
    fig.show()
    print("Please check the plot on your browser.")
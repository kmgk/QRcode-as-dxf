from qrcodegen import *
import ezdxf
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend


def main():
    # create dxf document
    doc = ezdxf.new("R2018", setup=True)
    msp = doc.modelspace()

    # create QR Code
    qr = QrCode.encode_text("QR Code as DXF", QrCode.Ecc.MEDIUM)

    for y in range(qr.get_size()):
        for x in range(qr.get_size()):
            if qr.get_module(x, y):
                # create polyline
                dot_polyline = msp.add_lwpolyline(
                    [
                        (x, qr.get_size() - y - 1),
                        (x + 1, qr.get_size() - y - 1),
                        (x + 1, qr.get_size() - y),
                        (x, qr.get_size() - y),
                        (x, qr.get_size() - y - 1),
                    ],
                    close=True,
                )
                # define hatch
                dot_hatch = msp.add_hatch()
                # create hatch from polyline
                dot_hatch.paths.add_polyline_path(
                    dot_polyline.get_points(format="xyb"), is_closed=True
                )

    # save as dxf
    doc.saveas("qrcode.dxf")

    # show dxf as picture
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(msp, finalize=True)
    plt.show()


if __name__ == "__main__":
    main()

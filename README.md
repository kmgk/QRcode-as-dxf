[ezdxf](https://github.com/mozman/ezdxf/tree/stable)と[nayuki/QR-Code-generator](https://github.com/nayuki/QR-Code-generator/tree/master/python)を使用してQRコードをdxfファイルとして描画し、保存することを目的とする。

## 実行環境
- OS: Windows 10
- Python: v3.10.7

## 使用するライブラリ
- ezdxf
    - 名前の通りdxfファイルの作成や編集を行う
    - `pip install ezdxf`
- [nayuki/QR-Code-generator](https://github.com/nayuki/QR-Code-generator/tree/master/python)
    - 文字列からQRコードを作成することが出来る
    - PyPIで[qrcodegen](https://pypi.org/project/qrcodegen/)として公開されているが、今回はローカルにダウンロードして使用
    - 以下このライブラリはqrcodegenとして表記
- matplotlib
    - 必須ではないが作成したdxfを保存せず確認することが可能
    - `pip install matplotlib`

## 文字列からQRコードを作成する
qrcodegenの`QrCode.encode_text`を使用することで文字列からQRコードを作成することができる。第二引数にはエラー訂正レベルを指定する必要があり、Low(7%)、Medium(15%)、Quartile(25%)、High(30%)の四種類の中から選ぶことができる。レベルを上げればQRコードが汚れていても読み取れる可能性が上がるが、QRコードのサイズが大きくなり読み取り時間も多くかかる。

```python
from qrcodegen import *
qr = QrCode.encode_text("こんにちは", QrCode.Ecc.LOW)
```
`get_size()`でQRコードのサイズ（縦横のドット数）、`get_module(x,y)`で(x,y)におけるQRコードの色が黒か白かをboolで取得できる（Trueは黒）。
```python
qr.get_size() # 21
qr.get_module(1, 1) # False
```
これらを組み合わせて、QRコードの情報を1つずつ取得していく。以下はQRコードの左上からドットの色を出力していくサンプル。あとはdxfにこれらの情報をオブジェクトとして書き出せばよい。
```python
# create QR Code
qr = QrCode.encode_text("QR Code as DXF", QrCode.Ecc.MEDIUM)

for y in range(qr.get_size()):
    for x in range(qr.get_size()):
        print(qr.get_module(x, y))
```

## QRコードをポリライン、ハッチで表現する
様々なやり方があるが、本稿ではQRコードを1ドットずつポリラインとハッチを組み合わせて描画していく。ドットはポリラインで閉じた正方形を描画し、その中をハッチで埋めることでドットを表現する。以下は一つのドットをポリラインとハッチで作成するサンプル。
```python
import ezdxf
# dxfドキュメントを作成
doc = ezdxf.new("R2018", setup=True)
msp = doc.modelspace()
# ポリラインの作成
dot_polyline = msp.add_lwpolyline([(0,0), (1,0), (1,1), (0,1), (0,0)], close=True)
# ハッチの定義
dot_hatch = msp.add_hatch()
# ポリラインに合わせてハッチを作成
dot_hatch.paths.add_polyline_path(
    dot_polyline.get_points(format="xyb"), is_closed=True
)
```
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/526555/0c18727b-d83d-7fb6-aba7-c33a44006272.png)

あとは生成したQRコードの情報をdxfに1つずつ描画していくだけ。dxfのアドオンとmatplotlibを使用してdxfを保存せずに確認することができる。注意点として、QRコードをforで1つずつ読み取るときは左上から読み取るが、インデックスは(x,y)=(0,0)からスタートするため`msp.add_lwpolyline([(x,y),(x+1,y),(x+1,y+1),(x,y+1),(x,y)], close=True)`で作成するとQRコードが上下逆になる。dxfファイルとして保存するには`doc.saveas("qrcode.dxf")`を使用する。

```python
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
```
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/526555/a5c83962-629a-0d1b-d803-789e820e6c65.png)

## 参考
- https://ezdxf.readthedocs.io/en/stable/index.html
- https://github.com/nayuki/QR-Code-generator/blob/master/python/qrcodegen.py
- https://qiita.com/Rai-see/items/aebf4587f7a9b30e3ab1
- https://www.nayuki.io/page/creating-a-qr-code-step-by-step

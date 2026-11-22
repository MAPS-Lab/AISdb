import inspect

import pytest

from aisdb.webdata import shore_dist
from aisdb.webdata.shore_dist import CoastDist, PortDist, ShoreDist


@pytest.mark.parametrize("raster_cls", [ShoreDist, PortDist, CoastDist])
def test_existing_tif_skips_download(raster_cls, tmp_path, monkeypatch):
    tif_filename = inspect.signature(raster_cls.__init__).parameters["tif_filename"].default
    (tmp_path / tif_filename).touch()

    def fail_download(*args, **kwargs):
        raise AssertionError("download_unzip called although the GeoTIFF exists")

    opened = []
    monkeypatch.setattr(shore_dist, "download_unzip", fail_download)
    monkeypatch.setattr(shore_dist.RasterFile, "__init__", lambda self, imgpath: opened.append(imgpath))

    raster_cls(data_dir=str(tmp_path))
    assert opened == [str(tmp_path / tif_filename)]

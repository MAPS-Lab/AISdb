# AISdb

> [!IMPORTANT]
> This repository is archived and no longer receives updates, fixes or releases. It stays available read-only for reference and citation. The published versions remain installable, but no new version will follow.

AISdb is an open-source database system for storing, retrieving, analyzing, and visualizing Automatic Identification System (AIS) data. It serves the data needs of the maritime domain, supporting research, development, and operational safety with a Python interface backed by a Rust core and SQLite or PostgreSQL/TimescaleDB storage. AISdb is developed and maintained by the [MAPS Lab](https://mapslab.tech/) at Dalhousie University, continuing work that began under the [MERIDIAN](https://meridian.cs.dal.ca) initiative.

## Features

- Efficient data management on SQLite and PostgreSQL/TimescaleDB, scaling from local files to server deployments
- A Python API usable across programming skill levels, with Rust handling decoding and other critical processing paths
- Data enrichment that joins AIS records with environmental, bathymetric, and weather datasets for marine context
- Analytical tools for complex queries, track processing, network graph generation, H3 spatial discretization, and statistical analysis directly against the database
- Dynamic visualization and export options in multiple formats for further analysis or reporting
- Modular design with optimized database schemas built for performance and scalability

AIS data comprises digital messages that ships and base stations transmit over VHF to exchange navigational and identification information. Messages arrive in standardized types covering dynamic position reports, static vessel metadata, and safety-related traffic, collected by on-shore antennas or low-orbit satellites. Beyond vessel tracking, this data underpins maritime research, environmental monitoring, and route optimization. Useful primers include the [AIS message types reference](https://arundaleais.github.io/docs/ais/ais_message_types.html), the [US Navigation Center](https://navcen.uscg.gov/ais-messages), the [IMO page on AIS transponders](https://www.imo.org/en/ourwork/safety/pages/ais.aspx), and the [Wikipedia article](https://en.wikipedia.org/wiki/Automatic_identification_system).

## Services

Beyond the Python package, the repository contains the deployable pieces of a self-hosted AISdb stack, each in its own top-level folder.

- `receiver/` decodes live NMEA streams from an antenna or aggregator feed, persists them to a local SQLite or PostgreSQL database, and rebroadcasts to downstream clients
- `database_server/` serves vectorized vessel tracks from PostgreSQL over a WebSocket API
- `aisdb_web/` is the JavaScript and WebAssembly map front end bundled into the Python wheel
- `client_webassembly/` compiles the in-browser geometry processing used by the map

## Installation

```sh
python -m venv .venv  # Create and activate a virtual environment
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
pip install aisdb  # Install AISdb from PyPI
```

PyPI carries AISdb up to version 1.7.2. Release 1.8.0-alpha and the final state of this repository were never uploaded to PyPI, so build them from source as described under [Building from source](#building-from-source), checking out the `1.8.0-alpha` tag for the release itself.

From release 1.8.0-alpha on, AISdb uses TimescaleDB instead of vanilla PostgreSQL. TimescaleDB is an extension built on top of PostgreSQL, optimized for time-series data with automatic partitioning and compression. For best performance, tune the database with the TimescaleDB installer and configure 7-day data chunks.

## Quick start

Decode raw AIS messages into a local SQLite database, then query them back as vessel tracks.

```python
from datetime import datetime, timedelta

import aisdb

start = datetime(2021, 11, 1)
end = start + timedelta(days=1)

with aisdb.DBConn("ais.sqlite") as dbconn:
    aisdb.decode_msgs(
        filepaths=["aisdb/tests/testdata/test_data_20211101.nm4"],
        dbconn=dbconn,
        source="TESTING",
    )
    qry = aisdb.DBQuery(
        dbconn=dbconn,
        start=start,
        end=end,
        callback=aisdb.sqlfcn_callbacks.in_timerange_validmmsi,
    )
    for track in aisdb.TrackGen(qry.gen_qry(), decimate=False):
        print(track["mmsi"], len(track["time"]))
```

## Building from source

The maturin build also compiles the WebAssembly map client and bundles the web assets, so building AISdb needs Python 3.10 or newer, the Rust toolchain with the WebAssembly target and wasm-pack, and Node.js 20 with npm.

```sh
python -m venv .venv  # Create a virtual environment
source .venv/bin/activate  # Activation command for Windows `.venv\Scripts\activate`
git clone https://github.com/MAPS-Lab/AISdb.git && cd AISdb  # Clone the repository
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > install-rust.sh  # Install Rust
/bin/bash install-rust.sh -q -y  # Run Rust installer
rustup target add wasm32-unknown-unknown  # Add the WebAssembly target
cargo install --locked wasm-pack wasm-bindgen-cli wasm-opt  # Install the wasm build tools
pip install --upgrade maturin[patchelf]  # Install Maturin for building
maturin develop --release --extras=test  # Build AISdb package
```

Run the test suite with pytest. Many tests need a local PostgreSQL 17 server, and the TimescaleDB paths also need the TimescaleDB extension.

```sh
pytest ./aisdb/tests/ --maxfail=10
```

The Rust engine has its own checks, run from the `aisdb_lib` directory with `cargo fmt --check`, `cargo clippy --features sqlite,postgres`, and `cargo test --features sqlite,postgres`. The workflows in `.github/workflows/` record a working build on each platform. They built wheels for Linux, macOS, and Windows, smoke-tested the Linux wheel installation with uv, and ran the test suite against PostgreSQL 17 (with TimescaleDB on Linux and macOS).

## Raster data

Bathymetry, distance-to-shore, and distance-to-port rasters used by `aisdb.webdata` are downloaded on first use from the [data release](https://github.com/MAPS-Lab/AISdb/releases/tag/data-v1) of this repository.

## Documentation

[Documentation](https://aisviz.gitbook.io/documentation/) · [Tutorials](https://aisviz.gitbook.io/tutorials/) · [API reference](https://maps-lab.github.io/AISdb/) · [Website](https://aisviz.cs.dal.ca/)

## Related projects

- AISdb-lite is the PostGIS and TimescaleDB first variant that ingests all AIS messages into two global hypertables. Its repository is private, and its [API reference](https://maps-lab.github.io/AISdb-lite/) is public
- NOAA-Integrator acquires AIS data from NOAA Marine Cadastre and loads it into AISdb-aligned databases. Its repository is private
- [AISdb-Tutorials](https://github.com/MAPS-Lab/AISdb-Tutorials) collects notebooks with worked examples for AISdb workflows
- [AISdb-GitBook](https://github.com/MAPS-Lab/AISdb-GitBook) holds the Markdown source of the user guides published on GitBook

## Contributors

AISdb is the work of everyone who contributed to it.

<a href="https://github.com/MAPS-Lab/AISdb/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=MAPS-Lab/AISdb" alt="Avatars of the AISdb contributors" />
</a>

## Citation

If you use AISdb in your work, please cite it. Citation metadata lives in [CITATION.cff](CITATION.cff), and the BibTeX entry follows.

```bibtex
@software{AISdb2026,
  author    = {Smith, Matthew and Chen, Jinkun and Spadon, Gabriel and Song, Ruixin and Vaishnav and Tharwani, Jay Kumar},
  title     = {AISdb},
  year      = {2026},
  version   = {1.8.0-alpha},
  publisher = {MAPS Lab, Dalhousie University},
  url       = {https://github.com/MAPS-Lab/AISdb},
  license   = {AGPL-3.0}
}
```

## License

This project is distributed under the terms of the GNU Affero General Public License v3.0 (AGPL-3.0). See [LICENSE](LICENSE) for details.

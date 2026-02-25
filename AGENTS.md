# AGENTS.md

## Cursor Cloud specific instructions

### Overview

Inkscape is a C++20 desktop vector graphics editor built with CMake/Ninja using GTK4 and gtkmm-4.0. The codebase is ~714K lines of C/C++. There are no backend services, databases, or API servers — it is a pure desktop application.

### Building

Standard build commands are documented in `doc/building/linux.md`. Quick reference:

```bash
cd /workspace/build
ninja install          # incremental build + install
```

The build directory is `/workspace/build` with install prefix at `/workspace/build/install_dir`. CMake is configured with:
- `CMAKE_BUILD_TYPE=Debug`
- `WITH_INTERNAL_2GEOM=ON` (uses bundled lib2geom)
- `WITH_NLS=OFF` (translations submodule not available)
- GCC as both C and C++ compiler (Clang is the system default but lacks libstdc++ linkage — `cc`/`c++` have been set to `gcc`/`g++` via `update-alternatives`)

### Running Inkscape

A virtual framebuffer is required since there is no physical display:

```bash
export DISPLAY=:99
Xvfb :99 -screen 0 1280x1024x24 &>/dev/null &
```

Run the binary: `/workspace/build/install_dir/bin/inkscape`

CLI export example (no GUI needed): `inkscape input.svg --export-filename=output.png --export-type=png`

### Testing

```bash
cd /workspace/build
ninja tests                           # build test binaries
ctest --output-on-failure -j$(nproc)  # run all tests
```

Expect ~96% pass rate. Some CLI/PDF tests fail due to environment limitations (missing fonts, EGL warnings). The `libEGL warning: DRI3` messages are harmless and expected in a headless environment.

### Lint / Code quality

```bash
python3 buildtools/check_license_headers.py   # license header check
```

Clang-tidy and clang-format are available via `buildtools/clangtidy.sh` and `buildtools/codequality.sh`.

### Known gotchas

- **Submodules**: The git tree does not contain submodule commit references. Submodules (lib2geom, libcroco, libdepixelize, extensions, themes) must be cloned manually into their respective directories under `src/3rdparty/` and `share/`.
- **libdepixelize API mismatch**: The submodule's CMake alias uses `Depixelize::depixelize` (lowercase) but Inkscape's `src/CMakeLists.txt` references `Depixelize::Depixelize` (uppercase). The alias has been fixed in `src/3rdparty/libdepixelize/CMakeLists.txt`. Additionally, `src/trace/depixelize/inkscape-depixelize.cpp` was adapted to use the new `Depixelize::Image` struct instead of `Glib::RefPtr<Gdk::Pixbuf>`.
- **Compiler defaults**: The system default `cc`/`c++` symlinks must point to `gcc`/`g++`, not clang, because the meson-based sub-builds (gtkmm, capypdf) fail when clang can't find libstdc++.
- **man page script**: `man/fix-roff-punct` needs execute permission (`chmod +x`).
- **Build time**: Full rebuild takes ~8-10 minutes with ccache cold. Incremental builds are fast.
- **gtkmm/capypdf**: These are built from source automatically by CMake's ExternalProject mechanism when the system versions are too old. This adds significant time to the first build.

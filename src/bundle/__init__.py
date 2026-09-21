"""The bundle: one agent's files, packed, signed and verified (SPEC/01 §2).

`src.bundle.pack` writes the archive; `src.bundle.verify` refuses one.
Nothing else here reads a bundle, and neither reads an envelope (P5).

Nothing is re-exported: `pack` and `verify` are the modules, and the
functions inside them have the same names.
"""

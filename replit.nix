
{ pkgs }: {
  deps = [
    pkgs.xcodebuild
    pkgs.grpc
    pkgs.which
    pkgs.gitFull
    pkgs.zlib
    pkgs.tk
    pkgs.tcl
    pkgs.libwebp
    pkgs.libtiff
    pkgs.libjpeg
    pkgs.libimagequant
    pkgs.lcms2
    pkgs.bash
    pkgs.xsimd
    pkgs.cacert
    pkgs.libxcrypt
    pkgs.libffi
    pkgs.rustc
    pkgs.pkg-config
    pkgs.libiconv
    pkgs.cargo
    pkgs.python310Full
    pkgs.openssh
    pkgs.redis
    pkgs.postgresql
    pkgs.xcbuild
    pkgs.swig
    pkgs.openjpeg
    pkgs.mupdf
    pkgs.libjpeg_turbo
    pkgs.jbig2dec
    pkgs.harfbuzz
    pkgs.gumbo
    pkgs.freetype
    pkgs.mailutils
    pkgs.sqlite-interactive
    pkgs.glibcLocales
    pkgs.openssl
    pkgs.git
    pkgs.gcc
    pkgs.cmake
    pkgs.ninja
  ];
  env = {
    PYTHONBIN = "${pkgs.python310Full}/bin/python3";
    LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.libjpeg_turbo
      pkgs.openjpeg
      pkgs.mupdf
    ];
  };
}

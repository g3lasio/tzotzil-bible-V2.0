{ pkgs }: {
  deps = [
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
    pkgs.python39Full
    pkgs.sqlite-interactive
    pkgs.glibcLocales
    pkgs.openssl
    pkgs.git
  ];
}

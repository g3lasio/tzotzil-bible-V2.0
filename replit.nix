
{ pkgs }: {
  deps = [
    pkgs.python39Full
    pkgs.openssh
    pkgs.redis
    pkgs.postgresql
    pkgs.xcbuild
    pkgs.swig
    pkgs.openjpeg
    pkgs.gumbo
    pkgs.freetype
    pkgs.mailutils
    pkgs.sqlite-interactive
    pkgs.glibcLocales
    pkgs.openssl
  ];
}

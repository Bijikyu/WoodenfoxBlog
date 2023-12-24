{pkgs}: {
  deps = [
    pkgs.libyaml
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.libyaml
    ];
  };
}

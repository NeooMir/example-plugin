project('neomir-plugins',
  version: '1.0.0',
  meson_version: '>= 0.60.0'
)

# Base plugins directory in system
plugins_install_dir = get_option('datadir') / 'neomir' / 'plugins' / 'example'

# 1. Install files directly to destination without tar
install_data(
  'example/plugin.json',
  install_dir: plugins_install_dir,
  install_mode: 'rw-r--r--',
)

install_data(
  'example/example_plugin.py',
  install_dir: plugins_install_dir,
  install_mode: 'rwxr-xr-x',
)

# 2. Standalone .plug packaging target (custom target, can be built via: ninja example.plug)
tar_prog = find_program('tar', required: false)

if tar_prog.found()
  custom_target('example-plug-package',
    input: [
      'example/plugin.json',
      'example/example_plugin.py',
    ],
    output: 'example.plug',
    command: [
      tar_prog,
      '-czf',
      '@OUTPUT@',
      '-C', meson.current_source_dir() / 'example',
      'plugin.json',
      'example_plugin.py',
    ],
    build_by_default: true,
  )
endif
